#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

from src.audit_batch import (
    estimate_batch_cost,
    run_audit_batch,
    run_audit_draft,
)
from src.data.corpus import load_document, scan_providers
from src.data.storage import init_db, load_objectives
from src.llm.client import get_openrouter_models
from src.review_bundle import render_result_section

_REGULATIONS = ["EU Data Act", "GDPR", "NIS2"]
_DEFAULT_MODEL = "google/gemini-3.8-flash"


def main():
    parser = argparse.ArgumentParser(
        description="Audit provider documents against codebook objectives and save results to reviews.db."
    )
    parser.add_argument("--regulation", choices=_REGULATIONS, required=True)
    parser.add_argument("--providers", nargs="+", default=["all"], metavar="NAME",
                        help='Provider folder names, or "all" (default).')
    parser.add_argument("--objectives", nargs="+", default=["all"], metavar="TITLE",
                        help='Objective titles, or "all" (default).')
    parser.add_argument("--model", default=_DEFAULT_MODEL)
    parser.add_argument("--yes", action="store_true", help="Skip the cost confirmation prompt.")
    parser.add_argument("--estimate-only", action="store_true", help="Print the cost estimate and exit.")
    parser.add_argument("--openrouter-provider", nargs="+", metavar="TAG", default=None,
                        help="Pin OpenRouter provider routing order, e.g. --openrouter-provider "
                             "google-ai-studio/flex for Gemini's half-price flex tier (still caches "
                             "when the document is large enough).")
    parser.add_argument("--draft", metavar="PATH",
                        help="Run the grid but write results as JSON to PATH instead of saving. "
                             "Review/edit the file, then run scripts/approve_audit.py PATH.")
    args = parser.parse_args()

    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key and not args.estimate_only:
        sys.exit("Set OPENROUTER_API_KEY (e.g. in .env) first.")

    init_db()
    objectives_df = load_objectives(regulation=args.regulation)
    if objectives_df.empty:
        sys.exit(f"No objectives for {args.regulation}. Run scripts/generate_objectives.py first.")

    providers = _resolve(args.providers, scan_providers(), "provider")
    titles = _resolve(args.objectives, objectives_df["title"].tolist(), "objective")
    objectives = objectives_df[objectives_df["title"].isin(titles)].to_dict("records")

    models = get_openrouter_models()
    estimate = estimate_batch_cost(providers, objectives, models, args.model)
    routing_note = f" | openrouter_provider={','.join(args.openrouter_provider)}" if args.openrouter_provider else ""
    print(f"{len(providers)} providers x {len(objectives)} objectives = {estimate['calls']} calls | "
          f"model={args.model}{routing_note}")
    print(f"  ~{estimate['input_tokens']:,} input + {estimate['output_tokens']:,} output tokens")
    print(f"Estimated cost: ~${estimate['costs']['total_cost']:.4f}")
    if args.openrouter_provider:
        print("  note: this estimate uses standard-tier pricing; the actual cost with "
              "--openrouter-provider routing (and any prompt caching) may be lower.")

    if args.estimate_only:
        return
    if not args.yes and input("Proceed? [y/N] ").strip().lower() not in ("y", "yes"):
        sys.exit("Aborted.")

    print()
    provider_routing = (
        {"order": args.openrouter_provider, "allow_fallbacks": True}
        if args.openrouter_provider else None
    )
    if args.draft:
        _run_draft(api_key, providers, objectives, args, provider_routing)
    else:
        _run_sync(api_key, providers, objectives, models, args, provider_routing)


def _run_sync(api_key, providers, objectives, models, args, provider_routing=None):
    start = time.time()
    summary = run_audit_batch(
        api_key, providers, objectives, models, args.model,
        on_progress=_print_progress, provider_routing=provider_routing,
    )
    print(f"\n\nDone in {time.time() - start:.0f}s — {summary['completed']} saved, "
          f"{summary['failed']} failed, ${summary['cost']:.4f} spent.")


def _run_draft(api_key, providers, objectives, args, provider_routing=None):
    objectives_by_id = {o["id"]: o for o in objectives}
    writer = _IncrementalDraftWriter(args.draft, args.regulation, args.model, objectives_by_id)

    start = time.time()
    outcome = run_audit_draft(
        api_key, providers, objectives, args.model,
        on_progress=_print_draft_progress, on_result=writer.add,
        provider_routing=provider_routing,
    )
    print(f"\n\nGenerated {len(outcome['results'])} results in {time.time() - start:.0f}s "
          f"({outcome['failed']} failed).")

    n_providers = len({r["provider"] for r in outcome["results"]})
    print(f"{args.draft} and its review files (across {n_providers} providers) were written "
          f"incrementally to {writer.review_dir}/ as each result completed.")
    print(f"\nReview/edit {args.draft}, then approve with:\n"
          f"  python scripts/approve_audit.py {args.draft}")


def _write_audit_draft(path, results):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    drafted = [{key: value for key, value in result.items() if key != "explanation"} for result in results]
    path.write_text(json.dumps(drafted, indent=2, ensure_ascii=False))


def _write_review_unit(review_dir, regulation, result, objective, document):
    provider = result["provider"]
    title = objective["title"] if objective else f"[deleted objective {result['objective_id']}]"

    lines = [
        f"# {provider} — {title}",
        "",
        f"- Regulation: {regulation}",
        f"- Objective id: {result['objective_id']}",
        f"- AI score: {result['score']}",
        "",
        "## Source document",
        "",
        document,
        "",
        f"## Objective: {title}",
        "",
    ]

    section_lines, flags = render_result_section(objective, result, document)
    lines += section_lines

    filename = f"{provider}__obj{result['objective_id']}.md"
    (review_dir / filename).write_text("\n".join(lines))
    return filename, title, flags


def _write_summary_file(review_dir, draft_path, regulation, model, index, total_flags, n_results):
    summary_lines = [
        f"# Audit review — {regulation}",
        "",
        f"- Draft: `{draft_path}`",
        f"- Model: `{model}`",
        f"- Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"- Results: {n_results}",
        f"- Automated checks: {total_flags} flagged",
        "",
        "## Files",
        "",
    ]
    summary_lines += index if index else ["None."]
    (review_dir / "SUMMARY.md").write_text("\n".join(summary_lines))


def _write_audit_review_bundle(draft_path, regulation, model, results, objectives_by_id):
    doc_cache = {}

    def document_for(provider):
        if provider not in doc_cache:
            doc_cache[provider] = load_document(provider)
        return doc_cache[provider]

    review_dir = Path(draft_path).parent / f"{Path(draft_path).stem}_review"
    review_dir.mkdir(parents=True, exist_ok=True)

    index = []
    total_flags = 0
    for result in sorted(results, key=lambda r: (r["provider"], r["objective_id"])):
        objective = objectives_by_id.get(result["objective_id"])
        document = document_for(result["provider"])
        filename, title, flags = _write_review_unit(review_dir, regulation, result, objective, document)

        total_flags += len(flags)
        index.append(f"- `{filename}` — {result['provider']} / {title} ({len(flags)} flagged)")
        index += [f"  - {flag}" for flag in flags]

    _write_summary_file(review_dir, draft_path, regulation, model, index, total_flags, len(results))
    return review_dir


class _IncrementalDraftWriter:
    def __init__(self, draft_path, regulation, model, objectives_by_id):
        self.draft_path = Path(draft_path)
        self.regulation = regulation
        self.model = model
        self.objectives_by_id = objectives_by_id
        self.review_dir = self.draft_path.parent / f"{self.draft_path.stem}_review"
        self.review_dir.mkdir(parents=True, exist_ok=True)
        self.results = []
        self._units_by_key = {}
        self._doc_cache = {}

    def _document_for(self, provider):
        if provider not in self._doc_cache:
            self._doc_cache[provider] = load_document(provider)
        return self._doc_cache[provider]

    def add(self, result):
        self.results.append(result)
        objective = self.objectives_by_id.get(result["objective_id"])
        document = self._document_for(result["provider"])
        unit = _write_review_unit(self.review_dir, self.regulation, result, objective, document)
        self._units_by_key[(result["provider"], result["objective_id"])] = unit

        _write_audit_draft(self.draft_path, self.results)
        self._refresh_summary()

    def _refresh_summary(self):
        index, total_flags = [], 0
        for result in sorted(self.results, key=lambda r: (r["provider"], r["objective_id"])):
            filename, title, flags = self._units_by_key[(result["provider"], result["objective_id"])]
            total_flags += len(flags)
            index.append(f"- `{filename}` — {result['provider']} / {title} ({len(flags)} flagged)")
            index += [f"  - {flag}" for flag in flags]
        _write_summary_file(self.review_dir, self.draft_path, self.regulation, self.model,
                            index, total_flags, len(self.results))


def _print_draft_progress(done, total):
    print(f"\r  {done}/{total}", end="", flush=True)


def _resolve(names, available, kind):
    if names == ["all"]:
        return available
    unknown = [n for n in names if n not in available]
    if unknown:
        sys.exit(f"Unknown {kind}(s): {', '.join(unknown)}\nAvailable: {', '.join(available)}")
    return names


def _print_progress(done, total, cost):
    print(f"\r  {done}/{total}   ${cost:.4f}", end="", flush=True)


if __name__ == "__main__":
    main()
