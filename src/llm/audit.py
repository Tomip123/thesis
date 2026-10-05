import json
import re

from openai import OpenAI

from src.analysis.regulation import article_number
from src.scoring import coverage_score

_BASE_URL = "https://openrouter.ai/api/v1"

_TIMEOUT = 120

_CLEAN_SOURCE_REF = re.compile(r"^Article\s+\d+(?:\s*\([^)]*\)|\s*[-–])*\s*$")

_CACHE_BREAKPOINT_MIN_CHARS = 4000


def _canonical_source_ref(llm_ref, article_ref):
    llm_ref = (llm_ref or "").strip()
    same_article = article_number(llm_ref) == article_number(article_ref)
    if same_article and _CLEAN_SOURCE_REF.match(llm_ref):
        return llm_ref
    return article_ref


def generate_objectives_from_article(api_key, article_text, article_ref,
                                     regulation_name="EU Data Act", model="openai/gpt-5-nano",
                                     existing_objectives=None, provider_routing=None):
    client = OpenAI(base_url=_BASE_URL, api_key=api_key, timeout=_TIMEOUT)

    if existing_objectives:
        covered = "\n".join(f"- {o['title']}: {o.get('description', '')}" for o in existing_objectives)
        exclusions = (
            "\n**ALREADY IN THE CODEBOOK — do NOT duplicate or lightly reword these:**\n"
            f"{covered}\n\n"
            "Only output thematic areas that are genuinely NOT covered above. If this "
            'article is already fully covered, return an empty "objectives" list.\n'
        )
    else:
        exclusions = ""

    prompt = f"""
    You are a Legal Content Strategist. Analyze {article_ref} of the {regulation_name}.
    Your goal is to synthesize its legal obligations into a concise set of 'High-Level Thematic Content Areas'.

    **Goal:** Instead of checking for strict compliance, we want to identify if provider contracts contain writings regarding specific thematic areas derived from the law.

    **CRITICAL ATOMICITY REQUIREMENT:**
    - Each Objective and each Criterion MUST be **atomic**.
    - **NEVER** use the word "and" or other conjunctions (or, as well as, along with) to combine multiple distinct requirements into one sentence.
    - If a legal clause has two requirements (e.g., "export data AND specify formats"), you MUST create TWO separate criteria.
    - This is essential because it is difficult for users to judge content that covers multiple distinct topics simultaneously.

    **Instructions:**
    1. **Identify Core Topics:** Group related legal obligations into single Thematic Content Areas (e.g., 'Data Export', 'Termination Rights').
    2. **Define the Area:** Write a clear, atomic title and description.
    3. **List Key Identification Topics:** For each area, list 3-5 specific, **atomic** topics or clauses that a provider's document should contain. Remember: **ONE TOPIC PER CRITERION. NO "AND"s.**
    4. **Scope:** Focus strictly on topics relevant for *Data Processing Services* (Cloud Providers).
    5. **Stay in scope:** Only derive objectives from {article_ref} itself. If it merely points to other articles, do NOT expand those — return few or no objectives.
    {exclusions}
    **Legal Text of {article_ref}:**
    {article_text}

    **Output Format (JSON only):**
    {{
        "objectives": [
            {{
                "title": "Short Atomic Title (e.g. Data Export Procedures)",
                "description": "The contract contains writings regarding...",
                "criteria": [
                    "Writings about data export structures.",
                    "Provisions regarding switching fees.",
                    "Timelines for data transfer."
                ],
                "source_ref": "The paragraph of {article_ref} this comes from, e.g. '{article_ref}(2)(a)'"
            }},
            ...
        ]
    }}
    """

    request = dict(
        model=model,
        messages=[
            {"role": "system", "content": "You are a senior legal content strategist. Output JSON only. You are obsessed with atomicity and avoid 'and' at all costs."},
            {"role": "user", "content": prompt},
        ],
        response_format={"type": "json_schema", "json_schema": {
            "name": "objective_generation",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "objectives": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "criteria": {"type": "array", "items": {"type": "string"}},
                                "source_ref": {"type": "string"},
                            },
                            "required": ["title", "description", "criteria", "source_ref"],
                            "additionalProperties": False,
                        },
                    }
                },
                "required": ["objectives"],
                "additionalProperties": False,
            },
        }},
    )
    if provider_routing:
        request["extra_body"] = {"provider": provider_routing}

    try:
        response = client.chat.completions.create(**request)
        objectives = json.loads(response.choices[0].message.content).get("objectives", [])
        for objective in objectives:
            objective["source_ref"] = _canonical_source_ref(objective.get("source_ref"), article_ref)
        return objectives
    except Exception as e:
        return [{"error": str(e)}]


def format_objective_audit_prompt(objective, context):
    numbered_criteria = "\n".join(f"{i}: {c}" for i, c in enumerate(objective['criteria']))

    system_msg = "You are a precise Legal Content Analyst. Return JSON only."
    document_block = f"    **Document Text:**\n    {context}\n"
    checklist_block = f"""
    ---

    You are a Lead Legal Content Analyst.
    Your task is to analyze the Cloud Provider's contract above to determine if there are specific writings regarding a high-level Objective.

    **Objective:** {objective['title']}
    **Description:** {objective['description']}

    **Numbered Topics to Look For (Checklist):**
    {numbered_criteria}

    **Instructions:**
    1. Scan the document to see if it contains writings, clauses, or terms regarding each item in the checklist.
    2. A checklist item is 'Covered' if the document explicitly addresses the topic, even if not fully compliant.
    3. Provide a list of the **indices** (0, 1, 2...) of the checklist items that were 'Covered'.
    4. Extract exact quotes to support your findings.

    **Output Format (JSON):**
    {{
        "met_criteria_indices": [0, 2],
        "explanation": "The provider includes detailed writings regarding topic 0 and 2...",
        "quotes": ["Clause 5.1...", "Clause 9..."]
    }}
    """

    document_part = {"type": "text", "text": document_block}
    if len(context) >= _CACHE_BREAKPOINT_MIN_CHARS:
        document_part["cache_control"] = {"type": "ephemeral"}
    return system_msg, [document_part, {"type": "text", "text": checklist_block}]


def audit_prompt_text(user_content):
    return "".join(part["text"] for part in user_content)


_ANALYSIS_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "analysis_result",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "met_criteria_indices": {"type": "array", "items": {"type": "integer"}},
                "explanation": {"type": "string"},
                "quotes": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["met_criteria_indices", "explanation", "quotes"],
            "additionalProperties": False,
        },
    },
}


def build_objective_analysis_request(objective, document_text):
    system_msg, user_content = format_objective_audit_prompt(objective, document_text)
    return {
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_content},
        ],
        "response_format": _ANALYSIS_RESPONSE_FORMAT,
    }


def parse_objective_analysis_result(content, objective):
    result = json.loads(content)
    criteria = objective.get("criteria", [])
    indices = result.pop("met_criteria_indices", [])
    result["met_criteria"] = [criteria[i] for i in dict.fromkeys(indices) if i < len(criteria)]
    result["score"] = coverage_score(result["met_criteria"], criteria)
    return result


def run_objective_analysis(api_key, document_text, objective, model="openai/gpt-5-nano",
                           provider_routing=None):
    client = OpenAI(base_url=_BASE_URL, api_key=api_key, timeout=_TIMEOUT)
    request = build_objective_analysis_request(objective, document_text)
    if provider_routing:
        request["extra_body"] = {"provider": provider_routing}

    try:
        response = client.chat.completions.create(model=model, **request)
        result = parse_objective_analysis_result(response.choices[0].message.content, objective)
        if getattr(response, "usage", None):
            result["_usage"] = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
            }
        return result
    except Exception as e:
        return {"error": str(e)}
