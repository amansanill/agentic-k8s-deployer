import json
from generator_agent.prompt import GENERATOR_PROMPT
from generator_agent.llm_client import call_llm
from shared.logger import log

def generate_intent(context: str) -> dict:
    log("Generator", "Building LLM prompt")

    prompt = f"{GENERATOR_PROMPT}\n\n{context}"

    log("Generator", "Calling LLM (Gemma via Ollama)")
    raw = call_llm(prompt)

    log("Generator", "Raw LLM response received")

    # ---------------- Robust JSON extraction ----------------
    json_lines = []
    inside_json = False

    for line in raw.splitlines():
        line = line.strip()

        if line.startswith("{"):
            inside_json = True
            json_lines.append(line)
            continue

        if inside_json:
            json_lines.append(line)

        if inside_json and line.endswith("}"):
            break

    json_text = "\n".join(json_lines)

    log("Generator", "Extracted JSON block:")
    for l in json_lines:
        log("Generator", l)

    try:
        intent = json.loads(json_text)
        log("Generator", "Intent JSON parsed successfully")
        return intent
    except json.JSONDecodeError as e:
        log("Generator", "ERROR: Invalid JSON from LLM")
        raise ValueError(f"Invalid JSON from LLM:\n{json_text}") from e
