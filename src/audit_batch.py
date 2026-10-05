import concurrent.futures

from src.data.corpus import load_document
from src.data.storage import save_objective_result
from src.llm.audit import (
    audit_prompt_text,
    format_objective_audit_prompt,
    run_objective_analysis,
)
from src.llm.client import count_tokens
from src.llm.costs import calculate_detailed_cost

_OUTPUT_TOKENS_PER_AUDIT = 1000
_INPUT_SAFETY_BUFFER = 1.2


def _split_priming_wave(pairs, contexts):
    heads, tails = [], []
    seen = set()
    for provider, objective in pairs:
        key = (provider, contexts[(provider, objective["id"])])
        if key in seen:
            tails.append((provider, objective))
        else:
            seen.add(key)
            heads.append((provider, objective))
    return heads, tails


def _run_pairs(api_key, pairs, contexts, model, provider_routing, on_result, should_cancel=None, on_progress=None):
    total = len(pairs)
    heads, tails = _split_priming_wave(pairs, contexts)
    done = failed = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        def run_wave(wave_pairs):
            nonlocal done, failed
            future_map = {}
            for provider, objective in wave_pairs:
                if should_cancel and should_cancel():
                    break
                future = executor.submit(
                    run_objective_analysis, api_key, contexts[(provider, objective["id"])], objective, model,
                    provider_routing=provider_routing,
                )
                future_map[future] = (provider, objective)

            for future in concurrent.futures.as_completed(future_map):
                if should_cancel and should_cancel():
                    break
                provider, objective = future_map[future]
                result = future.result()

                if "error" in result:
                    failed += 1
                else:
                    on_result(provider, objective, result)

                done += 1
                if on_progress:
                    on_progress(done, total)

        run_wave(heads)
        run_wave(tails)

    return done, failed


def run_audit_batch(api_key, providers, objectives, models_data, model,
                    on_progress=None, should_cancel=None, provider_routing=None):
    pairs = [(p, obj) for p in providers for obj in objectives]
    pricing = models_data.get(model, {"prompt": 0, "completion": 0})
    contexts = _resolve_contexts(pairs, {p: load_document(p) for p in providers})

    cost = 0.0

    def _save(provider, objective, result):
        nonlocal cost
        result["regulation"] = objective.get("regulation", "EU Data Act")
        save_objective_result(provider, objective["id"], result)
        usage = result.get("_usage", {})
        cost += usage.get("prompt_tokens", 0) * pricing.get("prompt", 0)
        cost += usage.get("completion_tokens", 0) * pricing.get("completion", 0)

    def _progress(done, total):
        if on_progress:
            on_progress(done, total, cost)

    done, failed = _run_pairs(api_key, pairs, contexts, model, provider_routing, _save, should_cancel, _progress)
    return {"completed": done - failed, "failed": failed, "cost": cost}


def run_audit_draft(api_key, providers, objectives, model,
                    on_progress=None, on_result=None, should_cancel=None,
                    provider_routing=None):
    pairs = [(p, obj) for p in providers for obj in objectives]
    contexts = _resolve_contexts(pairs, {p: load_document(p) for p in providers})

    results = []

    def _collect(provider, objective, result):
        row = {
            "provider": provider,
            "objective_id": objective["id"],
            "regulation": objective.get("regulation", "EU Data Act"),
            "score": result.get("score", 0),
            "met_criteria": result.get("met_criteria", []),
            "explanation": result.get("explanation", ""),
            "quotes": result.get("quotes", []),
        }
        results.append(row)
        if on_result:
            on_result(row)

    def _progress(done, total):
        if on_progress:
            on_progress(done, total)

    done, failed = _run_pairs(api_key, pairs, contexts, model, provider_routing, _collect, should_cancel, _progress)
    return {"completed": done - failed, "failed": failed, "results": results}


def estimate_batch_cost(providers, objectives, models_data, model):
    pairs = [(p, obj) for p in providers for obj in objectives]
    contexts = _resolve_contexts(pairs, {p: load_document(p) for p in providers})

    input_tokens = 0
    sample = None
    for provider, objective in pairs:
        context = contexts[(provider, objective["id"])]
        system_msg, user_content = format_objective_audit_prompt(objective, context)
        user_msg = audit_prompt_text(user_content)
        input_tokens += count_tokens(system_msg, model=model) + count_tokens(user_msg, model=model)
        if sample is None:
            sample = (provider, objective["title"], system_msg, user_msg, context)

    buffered_input = int(input_tokens * _INPUT_SAFETY_BUFFER)
    output_tokens = len(pairs) * _OUTPUT_TOKENS_PER_AUDIT
    costs = calculate_detailed_cost(model, models_data, buffered_input, output_tokens)
    return {
        "calls": len(pairs),
        "input_tokens": buffered_input,
        "output_tokens": output_tokens,
        "costs": costs,
        "sample": sample,
    }


def _resolve_contexts(pairs, full_docs):
    return {(provider, objective["id"]): full_docs[provider] for provider, objective in pairs}
