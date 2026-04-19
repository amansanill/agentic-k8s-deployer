import subprocess
from shared.logger import log

def call_llm(prompt: str) -> str:
    """
    Calls Ollama with Gemma and returns RAW output.
    NO streaming logs here — raw output must stay clean.
    """

    log("LLM", "Invoking Gemma via Ollama")

    full_prompt = f"""
SYSTEM:
You are a JSON generator.
Output ONLY valid JSON.
No explanations. No markdown.

USER:
{prompt}
"""

    result = subprocess.run(
        ["ollama", "run", "gemma", full_prompt],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr)

    # ⚠️ DO NOT log result.stdout line-by-line
    # That corrupts JSON

    return result.stdout.strip()
