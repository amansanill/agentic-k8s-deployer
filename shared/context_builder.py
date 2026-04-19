import os

def build_context(repo_path: str) -> str:
    context = ""

    dockerfile = os.path.join(repo_path, "Dockerfile")
    if os.path.exists(dockerfile):
        with open(dockerfile) as f:
            context += "\n--- Dockerfile ---\n" + f.read()

    package = os.path.join(repo_path, "package.json")
    if os.path.exists(package):
        with open(package) as f:
            context += "\n--- package.json ---\n" + f.read()

    return context
