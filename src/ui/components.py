def criterion_is_met(criterion, met_criteria):
    return any(criterion.strip().lower() == m.strip().lower() for m in met_criteria)
