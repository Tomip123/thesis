#!/usr/bin/env python3
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

from src.analysis.regulation import get_article_text, list_all_articles
from src.codebook import (
    criteria_count_flags,
    duplicate_flags,
    print_criteria_flags,
    print_duplicate_flags,
)
from src.data.storage import init_db, load_objectives, save_objectives
from src.llm.audit import generate_objectives_from_article

_REGULATIONS = ["EU Data Act", "GDPR", "NIS2"]
_DEFAULT_MODEL = "google/gemini-3.8-flash"


def main():
    parser = argparse.ArgumentParser(
        description="Generate codebook objectives from regulation articles and save them to reviews.db."
    )
    parser.add_argument("--regulation", required=True, choices=_REGULATIONS)
    parser.add_argument("--articles", nargs="+", metavar="REF",
                        help='Article refs, e.g. "Article 28" "Article 32".')
    parser.add_argument("--model", default=_DEFAULT_MODEL)
    parser.add_argument("--openrouter-provider", nargs="+", metavar="TAG", default=None,
                        help="Pin OpenRouter provider routing order, e.g. --openrouter-provider "
                             "google-ai-studio/flex for Gemini's half-price flex tier (still caches "
                             "when the article text is large enough).")
    parser.add_argument("--list", action="store_true", help="List the regulation's articles and exit.")
    parser.add_argument("--dry-run", action="store_true", help="Generate and print, but do not save.")
    parser.add_argument("--draft", metavar="PATH",
                        help="Write generated objectives as JSON to PATH instead of saving. "
                             "Review/edit the file, then run scripts/approve_objectives.py PATH.")
    args = parser.parse_args()

    if args.list:
        for article in list_all_articles(regulation=args.regulation):
            print(article)
        return
    if not args.articles:
        parser.error("provide --articles, or --list to see the options")
    if args.dry_run and args.draft:
        parser.error("--dry-run and --draft are mutually exclusive (dry-run discards the output)")

    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        sys.exit("Set OPENROUTER_API_KEY (e.g. in .env) first.")

    provider_routing = (
        {"order": args.openrouter_provider, "allow_fallbacks": True}
        if args.openrouter_provider else None
    )
    if args.openrouter_provider:
        print(f"openrouter_provider={','.join(args.openrouter_provider)}")

    init_db()
    existing_df = load_objectives(regulation=args.regulation)
    existing = existing_df[["title", "description"]].to_dict("records") if not existing_df.empty else []

    generated = []
    per_article = []
    for ref in args.articles:
        ref = ref.split(":")[0].strip()
        text = get_article_text(ref, regulation=args.regulation)
        if not text:
            print(f"! {ref}: not found in {args.regulation}, skipping")
            continue

        print(f"· {ref}: generating ...")
        objectives = generate_objectives_from_article(
            api_key, text, ref, regulation_name=args.regulation, model=args.model,
            existing_objectives=existing, provider_routing=provider_routing,
        )
        if objectives and "error" in objectives[0]:
            print(f"! {ref}: {objectives[0]['error']}")
            continue
        for objective in objectives:
            objective["regulation"] = args.regulation
        per_article.append((ref, text, objectives))
        generated.extend(objectives)

    if not generated:
        sys.exit("Nothing generated.")

    for objective in generated:
        print(f"    - {objective['title']}  ({objective['source_ref']}, {len(objective['criteria'])} criteria)")

    flags = duplicate_flags(generated, existing)
    count_flags = criteria_count_flags(generated)

    if args.dry_run:
        print(f"\n[dry run] {len(generated)} objectives NOT saved.")
        print_duplicate_flags(flags, saved=None)
        print_criteria_flags(count_flags)
        return

    if args.draft:
        _write_draft(args.draft, generated)
        review_dir = _write_review_bundle(
            args.draft, args.regulation, args.model, per_article, existing_df, flags, count_flags,
        )
        print(f"\nWrote {len(generated)} objectives to {args.draft} — NOT saved yet.")
        print(f"Wrote {len(per_article)} per-article review files to {review_dir}/.")
        print_duplicate_flags(flags, saved=None)
        print_criteria_flags(count_flags)
        print(f"\nReview/edit {args.draft}, then approve with:\n"
              f"  python scripts/approve_objectives.py {args.draft}")
        return

    save_objectives(generated)
    print(f"\nSaved {len(generated)} objectives to reviews.db.")
    print_duplicate_flags(flags, saved=load_objectives(regulation=args.regulation))
    print_criteria_flags(count_flags)


def _write_draft(path, objectives):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(objectives, indent=2, ensure_ascii=False))


def _write_review_bundle(draft_path, regulation, model, per_article, existing_df, flags, count_flags):
    flags_by_candidate = {}
    for candidate, match, score in flags:
        flags_by_candidate.setdefault(id(candidate), []).append((match, score))
    count_by_objective = {id(o): count for o, count in count_flags}

    review_dir = Path(draft_path).parent / f"{Path(draft_path).stem}_review"
    review_dir.mkdir(parents=True, exist_ok=True)

    index = []
    total_flags = 0
    for ref, text, objectives in per_article:
        sibling_objectives = [o for other_ref, _, objs in per_article if other_ref != ref for o in objs]

        existing_lines = [f"## Existing {regulation} objectives — check for semantic overlap", ""]
        if existing_df.empty and not sibling_objectives:
            existing_lines.append("(none yet)")
        else:
            if not existing_df.empty:
                existing_lines.append(f"### Already saved in reviews.db ({len(existing_df)})")
                existing_lines.append("")
                for _, row in existing_df.sort_values("id").iterrows():
                    existing_lines.append(f"- [{int(row['id'])}] **{row['title']}** — {row['description']}")
                existing_lines.append("")
            if sibling_objectives:
                existing_lines.append(
                    f"### Generated by other articles in this same run, not yet saved ({len(sibling_objectives)})"
                )
                existing_lines.append("")
                for o in sibling_objectives:
                    existing_lines.append(f"- **{o['title']}** ({o['source_ref']}) — {o['description']}")

        lines = [
            f"# {ref} — objective generation review",
            "",
            f"- Regulation: {regulation}",
            f"- Model: `{model}`",
            "",
            f"## {ref} — full text",
            "",
            text.strip(),
            "",
            f"## Generated objectives ({len(objectives)})",
            "",
        ]

        file_flags = []
        for i, objective in enumerate(objectives, start=1):
            lines += [
                f"### {i}. {objective['title']}  _{objective['source_ref']}, "
                f"{len(objective['criteria'])} criteria_",
                "",
                f"**Description:** {objective['description']}",
                "",
                "**Criteria:**",
            ]
            lines += [f"{j}. {c}" for j, c in enumerate(objective["criteria"])]
            lines.append("")

            for match, score in flags_by_candidate.get(id(objective), []):
                file_flags.append(f"{objective['title']!r} ≈ {match['title']!r}  (overlap {score:.2f})")
            if id(objective) in count_by_objective:
                file_flags.append(f"{count_by_objective[id(objective)]} criteria — "
                                   f"{objective['title']!r}  (aim for 3-6)")

        lines.append("## Flags")
        lines.append("")
        lines += [f"- {f}" for f in file_flags] if file_flags else ["None."]
        lines.append("")
        lines += existing_lines

        filename = f"{ref.replace(' ', '_')}.md"
        (review_dir / filename).write_text("\n".join(lines))

        total_flags += len(file_flags)
        index.append(f"- `{filename}` — {ref} ({len(objectives)} objectives, {len(file_flags)} flagged)")

    summary_lines = [
        f"# Objective generation review — {regulation}",
        "",
        f"- Draft: `{draft_path}`",
        f"- Model: `{model}`",
        f"- Generated: {datetime.now().isoformat(timespec='seconds')}",
        f"- Articles: {len(per_article)}",
        f"- Automated checks: {total_flags} flagged",
        "",
        "## Files",
        "",
    ]
    summary_lines += index if index else ["None."]
    (review_dir / "SUMMARY.md").write_text("\n".join(summary_lines))

    return review_dir


if __name__ == "__main__":
    main()
