import re

_WORD = re.compile(r"[a-z0-9]+")

_BODY_THRESHOLD = 0.38
_TITLE_THRESHOLD = 0.40
_TITLE_BODY_FLOOR = 0.25

_MIN_CRITERIA = 3
_MAX_CRITERIA = 6


def _tokens(text):
    return set(_WORD.findall((text or "").lower()))


def _body_tokens(objective):
    parts = [objective.get("title", ""), objective.get("description", "")]
    parts.extend(objective.get("criteria") or [])
    return _tokens(" ".join(parts))


def _jaccard(a, b):
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def duplicate_score(a, b):
    body = _jaccard(_body_tokens(a), _body_tokens(b))
    title = _jaccard(_tokens(a.get("title")), _tokens(b.get("title")))
    return body, title


def is_near_duplicate(a, b):
    body, title = duplicate_score(a, b)
    return body >= _BODY_THRESHOLD or (title >= _TITLE_THRESHOLD and body >= _TITLE_BODY_FLOOR)


def duplicate_flags(candidates, existing):
    flags = []
    pool = list(existing)
    for candidate in candidates:
        best_match, best_body = None, 0.0
        for other in pool:
            if is_near_duplicate(candidate, other):
                body, _ = duplicate_score(candidate, other)
                if body >= best_body:
                    best_match, best_body = other, body
        if best_match is not None:
            flags.append((candidate, best_match, best_body))
        pool.append(candidate)
    return flags


def criteria_count_flags(objectives, low=_MIN_CRITERIA, high=_MAX_CRITERIA):
    flagged = []
    for objective in objectives:
        count = len(objective.get("criteria") or [])
        if count < low or count > high:
            flagged.append((objective, count))
    return flagged


def print_duplicate_flags(flags, saved=None):
    if not flags:
        return
    print(f"\n⚠  {len(flags)} objective(s) look like duplicates — review:")
    for candidate, match, score in flags:
        prefix = ""
        if saved is not None:
            row = saved[saved["title"] == candidate["title"]]
            if not row.empty:
                prefix = f"[{int(row.iloc[0]['id'])}] "
        print(f"   {prefix}{candidate['title']!r}  ≈  {match['title']!r}   (overlap {score:.2f})")


def print_criteria_flags(count_flags):
    if not count_flags:
        return
    print(f"\n⚠  {len(count_flags)} objective(s) have an unusual criteria count (aim for 3-6, "
          "so coverage scores stay comparable):")
    for objective, count in count_flags:
        print(f"   {count} criteria — {objective['title']!r}  ({objective['source_ref']})")
