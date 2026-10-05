import json
from pathlib import Path

from src.analysis.regulation import article_label
from src.scoring import coverage_score
from src.ui.matching import find_quote_match

REVIEW_DIR_SUFFIX = "_review"
_CORRECTION_KEYS = {"corrected_met_criteria"}


def render_result_section(objective, result, document):
    lines, flags = [], []
    if objective:
        lines.append("**Criteria:**")
        stale = [c for c in result["met_criteria"] if c not in objective["criteria"]]
        for criterion in objective["criteria"]:
            mark = "x" if criterion in result["met_criteria"] else " "
            lines.append(f"- [{mark}] {criterion}")
        if stale:
            flags.append(f"met_criteria has an entry that isn't one of the objective's own "
                         f"criteria: {stale[0]!r}")
        lines.append("")

    lines += [f"**Explanation:** {result.get('explanation', '')}", "", "**Quotes:**"]
    for quote in result["quotes"]:
        match = find_quote_match(document, quote)
        if match:
            start, end = match
            window_start, window_end = max(0, start - 150), min(len(document), end + 150)
            snippet = document[window_start:window_end].replace("\n", " ")
            lines.append(f"- {quote!r}\n  found: ...{snippet}...")
        else:
            lines.append(f"- {quote!r}  **NOT FOUND in the source document**")
            flags.append(f"quote not found: {quote[:60]!r}")
    lines.append("")
    return lines, flags


def review_dir_for(draft_path):
    draft_path = Path(draft_path)
    return draft_path.parent / f"{draft_path.stem}{REVIEW_DIR_SUFFIX}"


def unit_path(review_dir, provider, objective_id):
    return Path(review_dir) / f"{provider}__obj{objective_id}.md"


def read_unit_explanation(review_dir, provider, objective_id):
    path = unit_path(review_dir, provider, objective_id)
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    section = text.rfind("\n## Objective: ")
    start = text.find("\n**Explanation:** ", section)
    end = text.find("\n\n**Quotes:**", start)
    if section == -1 or start == -1 or end == -1:
        raise ValueError(f"{path} has no **Explanation:** section")
    return text[start + len("\n**Explanation:** "):end]


def corrections_path(review_dir, provider, objective_id):
    return Path(review_dir) / f"{provider}__obj{objective_id}.corrections.json"


def read_corrections(review_dir, provider, objective_id):
    path = corrections_path(review_dir, provider, objective_id)
    if not path.exists():
        return None
    try:
        correction = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"{path} is not valid JSON: {e}") from e
    if not isinstance(correction, dict) or set(correction) - _CORRECTION_KEYS:
        raise ValueError(f"{path} must be {{}} or hold only {sorted(_CORRECTION_KEYS)}, not {correction!r:.80}")
    if not isinstance(correction.get("corrected_met_criteria", []), list):
        raise ValueError(f"{path}: corrected_met_criteria must be a list")
    return correction


def write_corrections(review_dir, result, reviewed_met_criteria):
    review_dir = Path(review_dir)
    review_dir.mkdir(parents=True, exist_ok=True)
    path = corrections_path(review_dir, result["provider"], result["objective_id"])

    recorded = read_corrections(review_dir, result["provider"], result["objective_id"])
    if recorded is not None and not _audit_verdict_changed(recorded, result, reviewed_met_criteria):
        return path

    correction = {}
    if set(reviewed_met_criteria) != set(result.get("met_criteria", [])):
        correction["corrected_met_criteria"] = list(reviewed_met_criteria)

    path.write_text(json.dumps(correction))
    return path


def _audit_verdict_changed(recorded, result, reviewed_met_criteria):
    shown_met = recorded.get("corrected_met_criteria", result.get("met_criteria", []))
    return set(reviewed_met_criteria) != set(shown_met)


def apply_corrections(results, objectives_by_id, review_dir):
    corrected = unchanged = missing = 0
    for result in results:
        correction = read_corrections(review_dir, result["provider"], result["objective_id"])
        if correction is None:
            missing += 1
            continue
        if not correction:
            unchanged += 1
            continue

        if "corrected_met_criteria" in correction:
            objective = objectives_by_id.get(result["objective_id"])
            criteria = objective["criteria"] if objective else []
            result["met_criteria"] = correction["corrected_met_criteria"]
            result["score"] = coverage_score(result["met_criteria"], criteria)
        corrected += 1
    return corrected, unchanged, missing


def review_progress(results, review_dir):
    reviewed = sum(
        1 for r in results
        if corrections_path(review_dir, r["provider"], r["objective_id"]).exists()
    )
    return reviewed, len(results)


def article_corrections_path(review_dir, article_ref):
    return Path(review_dir) / f"{article_ref.replace(' ', '_')}.corrections.json"


def read_article_corrections(review_dir, article_ref):
    path = article_corrections_path(review_dir, article_ref)
    if not path.exists():
        return None
    try:
        correction = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        raise ValueError(f"{path} is not valid JSON: {e}") from e
    if not isinstance(correction, dict) or set(correction) - {"objectives"}:
        raise ValueError(f"{path} must be {{}} or hold only an 'objectives' list, not {correction!r:.80}")
    if correction and not isinstance(correction["objectives"], list):
        raise ValueError(f"{path} must be {{}} or hold an 'objectives' list")
    return correction


def group_objectives_by_article(objectives):
    groups = {}
    for objective in objectives:
        groups.setdefault(article_label(objective.get("source_ref")), []).append(objective)
    return groups


def write_article_corrections(review_dir, article_ref, reviewed_objectives, original_objectives):
    review_dir = Path(review_dir)
    review_dir.mkdir(parents=True, exist_ok=True)
    path = article_corrections_path(review_dir, article_ref)

    recorded = read_article_corrections(review_dir, article_ref)
    if recorded is not None and reviewed_objectives == recorded.get("objectives", original_objectives):
        return path

    if reviewed_objectives == original_objectives:
        correction = {}
        body = json.dumps(correction)
    else:
        correction = {"objectives": reviewed_objectives}
        body = json.dumps(correction, indent=2, ensure_ascii=False)

    path.write_text(body)
    return path


def apply_article_corrections(objectives, review_dir):
    corrected = unchanged = missing = 0
    by_article = {}
    for article_ref, article_objectives in group_objectives_by_article(objectives).items():
        correction = read_article_corrections(review_dir, article_ref)
        if correction is None:
            missing += 1
            by_article[article_ref] = article_objectives
        elif not correction:
            unchanged += 1
            by_article[article_ref] = article_objectives
        else:
            corrected += 1
            by_article[article_ref] = correction["objectives"]
    return by_article, corrected, unchanged, missing


def merged_objectives(by_article):
    return [objective for objectives in by_article.values() for objective in objectives]


def article_review_progress(objectives, review_dir):
    articles = group_objectives_by_article(objectives)
    reviewed = 0
    for ref in articles:
        try:
            reviewed += read_article_corrections(review_dir, ref) is not None
        except ValueError:
            pass
    return reviewed, len(articles)
