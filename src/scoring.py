def coverage_score(met_criteria, all_criteria):
    total = len(all_criteria)
    if not total:
        return 0
    known = set(all_criteria)
    met = {criterion for criterion in met_criteria if criterion in known}
    return round(100 * len(met) / total)
