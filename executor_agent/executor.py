import subprocess
import tempfile
import yaml
import os
import re
import json
from shared.logger import log
from shared.runner import run

DOCKERHUB_USER = os.environ.get("DOCKERHUB_USER")

if not DOCKERHUB_USER:
    raise RuntimeError("DOCKERHUB_USER environment variable not set")


def k8s_name(name: str) -> str:
    name = name.lower()
    name = re.sub(r"[^a-z0-9-]", "-", name)
    name = re.sub(r"-+", "-", name)
    return name.strip("-")


def deploy(intent: dict, repo_path: str):
    log("Executor", "Starting build & deploy stage")

    app = k8s_name(intent["app_name"])
    port = int(intent["port"])
    image = intent["image"]

    # ---------------- CLEANUP ----------------
    log("Executor", "Cleaning previous deployments")
    
    try:
        run(["kubectl", "delete", "deployment", app], "Executor")
    except:
        pass
    
    try:
        run(["kubectl", "delete", "service", app], "Executor")
    except:
        pass
    
    try:
        run(["kubectl", "delete", "deployment", "mysql"], "Executor")
    except:
        pass
    
    try:
        run(["kubectl", "delete", "service", "mysql"], "Executor")
    except:
        pass

    # ---------------- BUILD ----------------
    if intent.get("has_dockerfile"):
        log("Executor", "Dockerfile detected → building image")
    
        image = f"{DOCKERHUB_USER}/{app}:latest"
        run(["docker", "build", "-t", image, "."], "Executor", cwd=repo_path)
        run(["docker", "push", image], "Executor")
    
    else:
        if not image:
            raise ValueError("No Dockerfile and no image provided → cannot deploy")
    
        log("Executor", f"Using prebuilt image: {image}")

    db_name = "mom_pop_db"
    db_password = "Msois@123"

    resources = []

    # ---------------- DB LOGIC ----------------
    if intent.get("db_detected"):
        log("Executor", "Database detected → deploying MySQL")

        # ---------- SQL DETECTION ----------
        sql_file_path = None
        for root, _, files in os.walk(repo_path):
            for f in files:
                if f.endswith(".sql"):
                    sql_file_path = os.path.join(root, f)
                    break

        if sql_file_path:
            log("Executor", f"SQL file detected: {sql_file_path}")

            try:
                run(["kubectl", "delete", "configmap", f"{app}-sql"], "Executor")
            except:
                pass

            run([
                "kubectl", "create", "configmap", f"{app}-sql",
                f"--from-file=create-db.sql={sql_file_path}"
            ], "Executor")

        volumes = [
            {"name": "db-storage", "emptyDir": {}}
        ]

        volume_mounts = [
            {"name": "db-storage", "mountPath": "/var/lib/mysql"}
        ]

        if sql_file_path:
            volumes.append({
                "name": "init-sql",
                "configMap": {"name": f"{app}-sql"}
            })
            volume_mounts.append({
                "name": "init-sql",
                "mountPath": "/docker-entrypoint-initdb.d"
            })

        db_deployment = {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {"name": "mysql"},
            "spec": {
                "replicas": 1,
                "selector": {"matchLabels": {"app": "mysql"}},
                "template": {
                    "metadata": {"labels": {"app": "mysql"}},
                    "spec": {
                        "containers": [
                            {
                                "name": "mysql",
                                "image": "mysql:5.7",
                                "env": [
                                    {"name": "MYSQL_ROOT_PASSWORD", "value": db_password},
                                    {"name": "MYSQL_DATABASE", "value": db_name}
                                ],
                                "ports": [{"containerPort": 3306}],
                                "volumeMounts": volume_mounts
                            }
                        ],
                        "volumes": volumes
                    }
                }
            }
        }

        db_service = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {"name": "mysql"},
            "spec": {
                "selector": {"app": "mysql"},
                "ports": [{"port": 3306}]
            }
        }

        resources.extend([db_deployment, db_service])

        env_vars = [
            {"name": "DB_HOST", "value": "mysql"},
            {"name": "DB_NAME", "value": db_name},
            {"name": "DB_PASSWORD", "value": db_password}
        ]

    else:
        log("Executor", "No database detected → skipping DB")
        env_vars = []

    # ---------------- APP DEPLOYMENT ----------------
    app_deployment = {
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
                            "ports": [{"containerPort": port}],
                            "env": env_vars
                        }
                    ]
                }
            }
        }
    }

    app_service = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {"name": app},
        "spec": {
            "type": "NodePort",
            "selector": {"app": app},
            "ports": [{"port": 80, "targetPort": port}]
        }
    }

    resources.extend([app_deployment, app_service])

    # ---------------- APPLY ----------------
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        yaml.dump_all(resources, f)
        path = f.name

    run(["kubectl", "apply", "-f", path], "Executor")

    log("Executor", "Deployment completed successfully")

    # ---------------- GET ACCESS URL ----------------
    try:
        svc_json = subprocess.check_output(
            ["kubectl", "get", "svc", app, "-o", "json"]
        )
        svc = json.loads(svc_json)

        node_port = svc["spec"]["ports"][0]["nodePort"]

        node_ip = subprocess.check_output(
            ["kubectl", "get", "nodes", "-o", "jsonpath={.items[0].status.addresses[0].address}"]
        ).decode()

        log("Executor", f"🚀 Application is LIVE at: http://{node_ip}:{node_port}")

    except Exception as e:
        log("Executor", f"Could not fetch access URL: {e}")
