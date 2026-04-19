import subprocess
import tempfile
import yaml
import os
import re
import json
import time
from shared.logger import log
from shared.runner import run

DOCKERHUB_USER = os.environ.get("DOCKERHUB_USER")

if not DOCKERHUB_USER:
    raise RuntimeError("DOCKERHUB_USER environment variable not set")


def k8s_name(name: str) -> str:
    """
    Convert app names to RFC-1123 compliant Kubernetes names
    """
    name = name.lower()
    name = re.sub(r"[^a-z0-9-]", "-", name)
    name = re.sub(r"-+", "-", name)
    return name.strip("-")


def deploy(intent: dict, repo_path: str):
    log("Executor", "Starting build & deploy stage")

    raw_app = intent["app_name"]
    port = int(intent["port"])

    app = k8s_name(raw_app)
    image = f"{DOCKERHUB_USER}/{app}:latest"

    # ---------------- Docker build ----------------
    log("Executor", f"Building Docker image: {image}")
    run(["docker", "build", "-t", image, "."], "Executor", cwd=repo_path)

    # ---------------- Docker push ----------------
    log("Executor", f"Pushing image to Docker Hub: {image}")
    run(["docker", "push", image], "Executor")

    # ---------------- Kubernetes Deployment ----------------
    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": app},
        "spec": {
            "replicas": 1,
            "selector": {"matchLabels": {"app": app}},
            "template": {
                "metadata": {"labels": {"app": app}},
                "spec": {
                    "containers": [
                        {
                            "name": app,
                            "image": image,
                            "imagePullPolicy": "Always",
                            "ports": [{"containerPort": port}],
                        }
                    ]
                },
            },
        },
    }

    service = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": app},
        "spec": {
            "type": "NodePort",
            "selector": {"app": app},
            "ports": [{"port": 80, "targetPort": port}],
        },
    }

    # ---------------- Print YAMLs ----------------
    log("Executor", "Generated Deployment YAML")
    print(yaml.dump(deployment, sort_keys=False))

    log("Executor", "Generated Service YAML")
    print(yaml.dump(service, sort_keys=False))

    # ---------------- Apply YAML ----------------
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump_all([deployment, service], f)
        path = f.name

    log("Executor", "Applying Kubernetes manifests")
    run(["kubectl", "apply", "-f", path], "Executor")

    # ---------------- Fetch access info ----------------
    log("Executor", "Waiting for NodePort assignment")
    time.sleep(3)

    svc_json = subprocess.check_output(
        ["kubectl", "get", "svc", app, "-o", "json"], text=True
    )
    svc = json.loads(svc_json)
    node_port = svc["spec"]["ports"][0]["nodePort"]

    nodes_json = subprocess.check_output(
        ["kubectl", "get", "nodes", "-o", "json"], text=True
    )
    nodes = json.loads(nodes_json)
    node_ip = nodes["items"][0]["status"]["addresses"][0]["address"]

    log("Executor", "Deployment completed successfully")
    log("Executor", f"Application URL: http://{node_ip}:{node_port}")

    return {
        "node_ip": node_ip,
        "node_port": node_port,
        "service_name": app,
    }
