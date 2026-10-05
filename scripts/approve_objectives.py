#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.codebook import (
    criteria_count_flags,
    duplicate_flags,
    print_criteria_flags,
    print_duplicate_flags,
)
from src.data.storage import (
    HUMAN_VERIFIER,
    init_db,
    load_objectives,
    save_objectives,
)
from src.review_bundle import (
    apply_article_corrections,
    read_article_corrections,
    merged_objectives,
    review_dir_for,
)

_REQUIRED_KEYS = {"title", "description", "criteria", "source_ref"}
_DEFAULT_REGULATION = "EU Data Act"


def main():
    parser = argparse.ArgumentParser(
        description="Sync a reviewed codebook draft into reviews.db -- the one command that ends a review."
    )
    parser.add_argument("draft", metavar="DRAFT_PATH",
                        help="JSON file written by generate_objectives.py --draft.")
    parser.add_argument("--dry-run", action="store_true",
                        help="Re-check flags against the current codebook, but do not save.")
    parser.add_argument("--allow-partial", action="store_true",
                        help="Save even though some articles have not been reviewed (they stay unverified).")
    args = parser.parse_args()

    draft_path = Path(args.draft)
    objectives = load_draft(draft_path)
    if not objectives:
        sys.exit(f"{args.draft} contains no objectives.")

    init_db()
    review_dir = review_dir_for(draft_path)
    by_article = merge_review(objectives, review_dir, allow_partial=args.allow_partial)
    objectives = merged_objectives(by_article)
    validate_objectives(objectives, source=f"{review_dir}'s corrections")
    by_regulation = group_by_regulation(objectives)
    flags, count_flags = check_flags(by_regulation)

    for objective in objectives:
        print(f"    - {objective['title']}  ({objective['source_ref']}, "
              f"{len(objective['criteria'])} criteria, {objective.get('regulation', _DEFAULT_REGULATION)})")

    if args.dry_run:
        print(f"\n[dry run] {len(objectives)} objectives NOT saved.")
        print_duplicate_flags(flags, saved=None)
        print_criteria_flags(count_flags)
        return

    reviewed, unreviewed = _split_by_review(by_article, review_dir)
    if not save_objectives(reviewed, verified_by=HUMAN_VERIFIER) or not save_objectives(unreviewed):
        sys.exit("Saving to reviews.db failed -- nothing was written for at least part of this "
                 "draft. The draft file is unchanged; fix the error above and run this again.")

    draft_path.write_text(json.dumps(objectives, indent=2, ensure_ascii=False))
    print(f"\nSaved {len(objectives)} objectives to reviews.db, "
          f"{len(reviewed)} marked verified by '{HUMAN_VERIFIER}'. Wrote corrections into {draft_path}")
    for regulation in by_regulation:
        saved = load_objectives(regulation=regulation)
        regulation_flags = [f for f in flags if f[0].get("regulation", _DEFAULT_REGULATION) == regulation]
        print_duplicate_flags(regulation_flags, saved=saved)
    print_criteria_flags(count_flags)


def merge_review(objectives, review_dir, allow_partial=False):
    if not review_dir.is_dir():
        if not allow_partial:
            sys.exit(f"No review bundle at {review_dir} -- nothing has been reviewed.\n"
                     f"Review this draft in the app's Codebook review screen first, or pass "
                     f"--allow-partial to save the unreviewed objectives anyway.")
        print(f"! No review bundle at {review_dir}: saving {len(objectives)} unreviewed objectives.")
        return {ref: objs for ref, objs in [(None, objectives)]}

    by_article, corrected, unchanged, missing = apply_article_corrections(objectives, review_dir)
    print(f"{corrected + unchanged + missing} articles | {corrected} corrected | "
          f"{unchanged} unchanged (reviewer agreed) | {missing} not yet reviewed")
    print(f"{len(objectives)} objectives in the draft -> {len(merged_objectives(by_article))} after review")

    if missing and not allow_partial:
        sys.exit(f"\n{missing} article(s) have no .corrections.json yet.\n"
                 f"Finish them in the app's Codebook review screen, or pass --allow-partial to save "
                 f"now and leave those objectives unverified.")
    return by_article


def _split_by_review(by_article, review_dir):
    reviewed, unreviewed = [], []
    for article_ref, objectives in by_article.items():
        has_verdict = bool(article_ref) and read_article_corrections(review_dir, article_ref) is not None
        (reviewed if has_verdict else unreviewed).extend(objectives)
    return reviewed, unreviewed


def load_draft(path):
    if not path.exists():
        sys.exit(f"No such draft file: {path}")
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        sys.exit(f"{path} is not valid JSON: {e}")

    validate_objectives(data, source=str(path))
    return data


def validate_objectives(objectives, source):
    for i, objective in enumerate(objectives):
        if not isinstance(objective, dict):
            sys.exit(f"{source}: entry #{i} is not an objective object.")
        missing = _REQUIRED_KEYS - objective.keys()
        if missing:
            sys.exit(f"{source}: objective #{i} ({objective.get('title', '?')!r}) "
                      f"is missing required field(s): {sorted(missing)}")
        if not isinstance(objective["criteria"], list):
            sys.exit(f"{source}: objective #{i} ({objective.get('title', '?')!r}) "
                      f"has criteria that are not a list.")


def group_by_regulation(objectives):
    groups = {}
    for objective in objectives:
        groups.setdefault(objective.get("regulation", _DEFAULT_REGULATION), []).append(objective)
    return groups


def check_flags(by_regulation):
    flags, count_flags = [], []
    for regulation, group in by_regulation.items():
        existing_df = load_objectives(regulation=regulation)
        own_keys = {(o["title"], o["source_ref"], regulation) for o in group}
        existing = [
            {"title": row["title"], "description": row["description"]}
            for _, row in existing_df.iterrows()
            if (row["title"], row["source_ref"], regulation) not in own_keys
        ] if not existing_df.empty else []
        flags.extend(duplicate_flags(group, existing))
        count_flags.extend(criteria_count_flags(group))
    return flags, count_flags


if __name__ == "__main__":
    main()
