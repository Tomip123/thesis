def calculate_detailed_cost(model_id, models_data, total_input_tokens, total_output_tokens):
    costs = {"input_cost": 0.0, "output_cost": 0.0, "total_cost": 0.0}

    if model_id in models_data:
        pricing = models_data[model_id]
        costs["input_cost"] = total_input_tokens * pricing["prompt"]
        costs["output_cost"] = total_output_tokens * pricing["completion"]

    costs["total_cost"] = costs["input_cost"] + costs["output_cost"]
    return costs
