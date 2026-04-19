import os
import re


def build_context(repo_path: str):
    context_str = ""

    # ---------------- STRUCTURED CONTEXT ----------------
    context_dict = {
        "has_dockerfile": False,
        "has_compose": False,
        "compose_has_build": False,
        "compose_build_path": None,
        "has_sql_file": False,
        "db_detected": False,
        "db_type": None,
        "repo_name": os.path.basename(repo_path),
        "host_port": None,
        "container_port": None,
    }

    # ---------------- Dockerfile ----------------
    dockerfile_path = os.path.join(repo_path, "Dockerfile")
    if os.path.exists(dockerfile_path):
        context_dict["has_dockerfile"] = True
        with open(dockerfile_path) as f:
            context_str += "\n--- Dockerfile ---\n" + f.read()

    # ---------------- package.json ----------------
    package_path = os.path.join(repo_path, "package.json")
    if os.path.exists(package_path):
        with open(package_path) as f:
            context_str += "\n--- package.json ---\n" + f.read()

    # ---------------- requirements.txt ----------------
    requirements_path = os.path.join(repo_path, "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path) as f:
            context_str += "\n--- requirements.txt ---\n" + f.read()

    # ---------------- SQL DETECTION ----------------
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".sql"):
                context_dict["has_sql_file"] = True

    # ---------------- docker-compose ----------------
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.lower() in ["docker-compose.yml", "docker-compose.yaml"]:
                context_dict["has_compose"] = True
                compose_path = os.path.join(root, file)

                with open(compose_path) as f:
                    content = f.read()
                    context_str += "\n--- docker-compose.yaml ---\n" + content

                    # ---------------- PORT EXTRACTION ----------------
                    port_match = re.search(r'ports:\s*-\s*"?(\d+):(\d+)"?', content)
                    if port_match:
                        host_port = int(port_match.group(1))
                        container_port = int(port_match.group(2))

                        context_dict["host_port"] = host_port
                        context_dict["container_port"] = container_port

                        context_str += f"\n--- HOST_PORT: {host_port} ---\n"
                        context_str += f"\n--- CONTAINER_PORT: {container_port} ---\n"

                    # ---------------- BUILD DETECTION ----------------
                    if "build:" in content:
                        context_dict["compose_has_build"] = True

                        match_simple = re.search(r'build:\s*(\./\S+)', content)
                        match_context = re.search(r'context:\s*(\./\S+)', content)

                        if match_context:
                            context_dict["compose_build_path"] = match_context.group(1)
                        elif match_simple:
                            context_dict["compose_build_path"] = match_simple.group(1)

                    # ---------------- DB TYPE DETECTION ----------------
                    lower = content.lower()
                    if "mongo" in lower:
                        context_dict["db_type"] = "mongo"
                    elif "mysql" in lower:
                        context_dict["db_type"] = "mysql"
                    elif "postgres" in lower:
                        context_dict["db_type"] = "postgres"

    # ---------------- FINAL DB TRUTH ----------------
    context_dict["db_detected"] = context_dict["has_sql_file"]

    # ---------------- FLAGS FOR LLM ----------------
    context_str += f"\n--- HAS_DOCKERFILE: {context_dict['has_dockerfile']} ---\n"
    context_str += f"\n--- HAS_COMPOSE: {context_dict['has_compose']} ---\n"
    context_str += f"\n--- COMPOSE_HAS_BUILD: {context_dict['compose_has_build']} ---\n"
    context_str += f"\n--- HAS_SQL_FILE: {context_dict['has_sql_file']} ---\n"
    context_str += f"\n--- DB_DETECTED: {context_dict['db_detected']} ---\n"

    if context_dict["db_type"]:
        context_str += f"\n--- DB_TYPE: {context_dict['db_type']} ---\n"

    return context_str, context_dict
