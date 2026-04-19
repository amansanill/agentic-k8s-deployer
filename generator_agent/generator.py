import json
from shared.logger import log
from generator_agent.llm_client import call_llm


def generate_intent(context: str) -> dict:
    log("Generator", "Building LLM prompt")

    prompt = f"""
You are a deployment assistant.

STRICT RULES:
- Output ONLY valid JSON
- Do NOT guess values
- If unsure, use null
- port must be an integer
- db_detected must be true or false

Context:
{context}

Return JSON in this format:
{{
  "app_name": "",
  "image": "",
  "port": 80,
  "db_detected": false
}}
"""

    log("Generator", "Calling LLM")
    response = call_llm(prompt)

    log("Generator", "Raw LLM response received")

    # Extract JSON safely
    start = response.find("{")
    end = response.rfind("}") + 1
    json_str = response[start:end]

    intent = json.loads(json_str)

    log("Generator", f"Parsed intent: {intent}")
    return intent
