#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.storage import (
    HUMAN_VERIFIER,
    init_db,
    load_objectives,
    save_objective_result,
)
from src.review_bundle import (
    apply_corrections,
    read_corrections,
    read_unit_explanation,
    review_dir_for,
)
from src.scoring import coverage_score

_REQUIRED_KEYS = {"provider", "objective_id", "met_criteria"}
_DEFAULT_REGULATION = "EU Data Act"


def main():
    parser = argparse.ArgumentParser(
        description="Sync a reviewed audit draft into reviews.db -- the one command that ends a review."
    )
    parser.add_argument("draft", metavar="DRAFT_PATH", help="JSON file written by run_audit.py --draft.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be saved, with recomputed scores, but do not save.")
    parser.add_argument("--allow-partial", action="store_true",
                        help="Save even though some units have not been reviewed (they stay unverified).")
    args = parser.parse_args()

    draft_path = Path(args.draft)
    results = load_draft(draft_path)
    if not results:
        sys.exit(f"{args.draft} contains no results.")

    init_db()
    objectives_by_id = {row["id"]: row for row in load_objectives().to_dict("records")}

    review_dir = review_dir_for(draft_path)
    merge_review(draft_path, results, objectives_by_id, review_dir,
                 dry_run=args.dry_run, allow_partial=args.allow_partial)

    saved = skipped = verified = 0
    for result in results:
        objective = objectives_by_id.get(result["objective_id"])
        if objective is None:
            print(f"! {result['provider']} / objective {result['objective_id']}: "
                  f"no longer in the codebook, skipping")
            skipped += 1
            continue

        score = coverage_score(result["met_criteria"], objective["criteria"])
        print(f"    - {result['provider']:20s} {objective['title']:30s} score {score}")

        if not args.dry_run:
            reviewed = (review_dir.is_dir() and
                        read_corrections(review_dir, result["provider"], result["objective_id"]) is not None)
            explanation = read_unit_explanation(review_dir, result["provider"], result["objective_id"])
            save_objective_result(result["provider"], objective["id"], {
                "score": score,
                "met_criteria": result["met_criteria"],
                "explanation": explanation or "",
                "quotes": result.get("quotes", []),
                "regulation": result.get("regulation", objective.get("regulation", _DEFAULT_REGULATION)),
            }, verified_by=HUMAN_VERIFIER if reviewed else None)
            saved += 1
            verified += reviewed

    if args.dry_run:
        print(f"\n[dry run] {len(results)} results NOT saved ({skipped} would be skipped).")
    else:
        print(f"\nSaved {saved} results to reviews.db ({skipped} skipped), "
              f"{verified} marked verified by '{HUMAN_VERIFIER}'.")


def merge_review(draft_path, results, objectives_by_id, review_dir, dry_run=False, allow_partial=False):
    if not review_dir.is_dir():
        if not allow_partial:
            sys.exit(f"No review bundle at {review_dir} -- nothing has been reviewed.\n"
                     f"Review this draft in the app's Audit review screen first, or pass "
                     f"--allow-partial to save the unreviewed results anyway.")
        print(f"! No review bundle at {review_dir}: saving {len(results)} unreviewed results.")
        return len(results)

    corrected, unchanged, missing = apply_corrections(results, objectives_by_id, review_dir)
    print(f"{len(results)} results | {corrected} corrected | {unchanged} unchanged (reviewer agreed) "
          f"| {missing} not yet reviewed")

    if missing and not allow_partial:
        sys.exit(f"\n{missing} of {len(results)} results have no .corrections.json yet.\n"
                 f"Finish them in the app's Audit review screen, or pass --allow-partial to save now "
                 f"and leave those rows unverified.")

    if not dry_run:
        draft_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
        print(f"Wrote corrections into {draft_path}")
    return missing


def load_draft(path):
    if not path.exists():
        sys.exit(f"No such draft file: {path}")
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        sys.exit(f"{path} is not valid JSON: {e}")

    for i, result in enumerate(data):
        missing = _REQUIRED_KEYS - result.keys()
        if missing:
            sys.exit(f"{path}: result #{i} is missing required field(s): {sorted(missing)}")
    return data


if __name__ == "__main__":
    main()
