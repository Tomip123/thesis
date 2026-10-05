import requests

_FALLBACK_MODELS = {
    "google/gemini-3-flash-preview": {
        "name": "Gemini 3 Flash Preview",
        "prompt": 0.0000001, "completion": 0.0000004, "context_length": 1000000,
    },
    "openai/gpt-4o": {
        "name": "GPT-4o", "prompt": 0.0000025, "completion": 0.00001, "context_length": 128000,
    },
    "openai/gpt-4o-mini": {
        "name": "GPT-4o Mini", "prompt": 0.00000015, "completion": 0.0000006, "context_length": 128000,
    },
}


def get_openrouter_models():
    try:
        response = requests.get("https://openrouter.ai/api/v1/models")
        if response.status_code != 200:
            return dict(_FALLBACK_MODELS)

        models = {}
        for m in response.json().get("data", []):
            pricing = m.get("pricing", {})
            models[m["id"]] = {
                "name": m.get("name", m["id"]),
                "prompt": float(pricing.get("prompt", 0)),
                "completion": float(pricing.get("completion", 0)),
                "context_length": int(m.get("context_length", 0)) if m.get("context_length") else 0,
            }
        return models
    except Exception:
        return {"google/gemini-3-flash-preview": dict(_FALLBACK_MODELS["google/gemini-3-flash-preview"])}


def count_tokens(text, model="google/gemini-3-flash-preview"):
    try:
        import tiktoken

        model_name = model.split('/')[-1] if '/' in model else model
        if any(m in model_name for m in ["gpt-4", "gpt-3.5", "gpt-4o"]):
            try:
                encoding = tiktoken.encoding_for_model(model_name)
            except Exception:
                encoding = tiktoken.get_encoding("cl100k_base")
        else:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))
    except Exception:
        import re

        tokens = re.findall(r"[\w']+|[.,!?;:#$%-]", text)
        count = 0
        for t in tokens:
            if len(t) > 8:
                count += 1 + (len(t) // 4)
            else:
                count += 1
        return int(count * 1.1)
