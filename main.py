from shared.repo_reader import clone_repo
from shared.context_builder import build_context
from generator_agent.generator import generate_intent
from validator_agent.validator import validate_intent
from executor_agent.executor import deploy
from shared.logger import log

def main():
    repo_url = input("Enter GitHub repository URL: ").strip()

    log("Main", "Starting deployment pipeline")

    log("Main", "Cloning repository")
    repo_path = clone_repo(repo_url)

    log("Main", "Building repository context")
    context = build_context(repo_path)

    log("Main", "Generating intent using LLM")
    intent = generate_intent(context)

    log("Main", "Validating intent")
    intent = validate_intent(intent)

    log("Main", "Executing build & deploy")
    deploy(intent, repo_path)

    log("Main", "Pipeline finished successfully")

if __name__ == "__main__":
    main()
