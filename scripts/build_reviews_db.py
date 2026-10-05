#!/usr/bin/env python3
import argparse
import json
import os
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data import storage
from src.review_bundle import (
    apply_article_corrections,
    apply_corrections,
    merged_objectives,
    read_unit_explanation,
    review_dir_for,
)
from src.scoring import coverage_score

DEFAULT_OUT = "reviews.db"
CODEBOOK_DRAFTS = (
    "output/objective_drafts/nis2_clean.json",
    "output/objective_drafts/eu_data_act_clean.json",
    "output/objective_drafts/gdpr_clean.json",
)
AUDIT_DRAFTS = (
    "output/audit_drafts/nis2_audit.json",
    "output/audit_drafts/eu_data_act_audit.json",
    "output/audit_drafts/gdpr_audit.json",
)
_DEFAULT_REGULATION = "EU Data Act"
_OBJECTIVE_KEYS = {"title", "description", "criteria", "source_ref"}
_RESULT_KEYS = {"provider", "objective_id", "met_criteria"}


def _load_list(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"{path} should hold a list of drafts, not a {type(data).__name__}")
    if not data:
        raise ValueError(f"{path} holds no drafts -- a regulation would be missing from the database")
    return data


def _check_fields(path, entry, required, list_field):
    if not isinstance(entry, dict) or required - entry.keys():
        missing = sorted(required - entry.keys()) if isinstance(entry, dict) else sorted(required)
        raise ValueError(f"{path}: an entry is missing {missing}: {entry!r:.100}")
    values = entry[list_field]
    if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
        raise ValueError(f"{path}: {list_field} must be a list of texts in {entry!r:.100}")


def reviewed_codebook(draft_paths):
    objectives = []
    for path in draft_paths:
        by_article, _, _, missing = apply_article_corrections(_load_list(path), review_dir_for(path))
        if missing:
            raise ValueError(f"{path}: {missing} article(s) have no review verdict in "
                             f"{review_dir_for(path)} -- review them before building the database")
        for objective in merged_objectives(by_article):
            _check_fields(path, objective, _OBJECTIVE_KEYS, "criteria")
            objectives.append(objective)
    return objectives


def reviewed_results(draft_paths, objectives_by_id):
    results, corrected_total = [], 0
    for path in draft_paths:
        draft = _load_list(path)
        for result in draft:
            _check_fields(path, result, _RESULT_KEYS, "met_criteria")
        corrected, _, missing = apply_corrections(draft, objectives_by_id, review_dir_for(path))
        if missing:
            raise ValueError(f"{path}: {missing} unit(s) have no review verdict in "
                             f"{review_dir_for(path)} -- review them before building the database")
        for result in draft:
            _check_fits_objective(path, result, objectives_by_id)
            result["score"] = coverage_score(result["met_criteria"],
                                             objectives_by_id[result["objective_id"]]["criteria"])
            result["explanation"] = _unit_explanation(path, result)
        results += draft
        corrected_total += corrected
    return results, corrected_total


def _unit_explanation(path, result):
    explanation = read_unit_explanation(review_dir_for(path), result["provider"], result["objective_id"])
    if explanation is None:
        raise ValueError(f"{path}: {result['provider']} / objective {result['objective_id']} has no "
                         f"review file in {review_dir_for(path)}")
    return explanation


def _check_fits_objective(path, result, objectives_by_id):
    unit = f"{path}: {result.get('provider')} / objective {result.get('objective_id')}"
    objective = objectives_by_id.get(result.get("objective_id"))
    if objective is None:
        raise ValueError(f"{unit} is not in the codebook")
    regulation = result.get("regulation", _DEFAULT_REGULATION)
    if regulation != objective["regulation"]:
        raise ValueError(f"{unit} is a {regulation} result but the objective is {objective['regulation']}")
    stray = [c for c in result["met_criteria"] if c not in objective["criteria"]]
    if stray:
        raise ValueError(f"{unit} counts {stray[0]!r} as met, which is not one of the objective's "
                         f"criteria -- the drafts may not match the codebook's ids")


def _query(db_path, sql):
    with closing(sqlite3.connect(db_path)) as con:
        return con.execute(sql).fetchall()


def _write(db_path, objectives, audit_drafts):
    previous = storage.DB_PATH
    storage.DB_PATH = str(db_path)
    try:
        storage.init_db()
        if not storage.save_objectives(objectives):
            raise RuntimeError(f"saving the codebook into {db_path} failed")
        saved = _query(db_path, "SELECT id, title, source_ref, regulation FROM compliance_objectives "
                                "ORDER BY id")
        expected = [(position, o["title"], o["source_ref"], o.get("regulation", _DEFAULT_REGULATION))
                    for position, o in enumerate(objectives, start=1)]
        if saved != expected:
            raise RuntimeError(f"the codebook in {db_path} does not match the drafts: "
                               f"{len(saved)} rows saved for {len(objectives)} objectives (for "
                               f"example, two objectives with the same title, article and "
                               f"regulation become one row)")

        objectives_by_id = {position: dict(o, regulation=o.get("regulation", _DEFAULT_REGULATION))
                            for position, o in enumerate(objectives, start=1)}
        reviewed, corrected = reviewed_results(audit_drafts, objectives_by_id)
        for result in reviewed:
            storage.save_objective_result(result["provider"], result["objective_id"], {
                "score": result["score"],
                "met_criteria": result["met_criteria"],
                "explanation": result.get("explanation", ""),
                "quotes": result.get("quotes", []),
                "regulation": result.get("regulation", _DEFAULT_REGULATION),
            }, verified_by=storage.HUMAN_VERIFIER)
        [(count,)] = _query(db_path, "SELECT COUNT(*) FROM objective_results")
        if count != len(reviewed):
            raise RuntimeError(f"{count} of {len(reviewed)} results were saved into {db_path} "
                               f"(a provider and objective may appear twice in the drafts)")
        return len(reviewed), corrected
    finally:
        storage.DB_PATH = previous


def build(out=DEFAULT_OUT, codebook_drafts=CODEBOOK_DRAFTS, audit_drafts=AUDIT_DRAFTS, force=False):
    out = Path(out)
    if out.exists() and not force:
        raise FileExistsError(f"{out} already exists -- pass --force to replace it")
    if not out.parent.is_dir():
        raise FileNotFoundError(f"there is no folder {out.parent} to write {out.name} into")
    objectives = reviewed_codebook(codebook_drafts)
    temporary = out.with_name(out.name + ".building")
    temporary.unlink(missing_ok=True)
    try:
        n_results, corrected = _write(temporary, objectives, audit_drafts)
        os.replace(temporary, out)
    finally:
        temporary.unlink(missing_ok=True)
    return len(objectives), n_results, corrected


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Build reviews.db from the reviewed codebook and audit drafts and their review decisions.")
    parser.add_argument("--out", default=DEFAULT_OUT, help=f"the database to write (default: {DEFAULT_OUT})")
    parser.add_argument("--force", action="store_true", help="replace the database if it exists")
    args = parser.parse_args(argv)
    try:
        n_objectives, n_results, corrected = build(args.out, force=args.force)
    except (FileExistsError, FileNotFoundError, ValueError, RuntimeError) as error:
        sys.exit(f"Could not build {args.out}: {error}")
    print(f"{args.out}: {n_objectives} objectives and {n_results} results, every one with a "
          f"recorded review verdict ({corrected} results corrected in review)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
