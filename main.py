from shared.repo_reader import clone_repo
from shared.context_builder import build_context
from generator_agent.generator import generate_intent
from validator_agent.validator import validate_intent
from executor_agent.executor import deploy
from shared.logger import log


def main():
    repo_url = input("Enter GitHub repository URL: ").strip()

    log("Main", "Starting deployment pipeline")

    # ---------------- CLONE ----------------
    log("Main", "Cloning repository")
    repo_path = clone_repo(repo_url)

    # ---------------- CONTEXT ----------------
    log("Main", "Building repository context")

    # NEW (IMPORTANT)
    context_str, context_dict = build_context(repo_path)

    # ---------------- GENERATOR ----------------
    log("Main", "Generating intent using LLM")
    intent = generate_intent(context_str)

    # ---------------- VALIDATOR ----------------
    log("Main", "Validating intent")

    # PASS STRUCTURED CONTEXT (NOT STRING)
    intent = validate_intent(intent, context_dict)

    # ---------------- EXECUTOR ----------------
    log("Main", "Executing build & deploy")
    deploy(intent, repo_path)

    log("Main", "Pipeline finished successfully")


if __name__ == "__main__":
    main()
