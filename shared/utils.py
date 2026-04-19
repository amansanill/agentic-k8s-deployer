import re
import yaml

def sanitize_name(name: str) -> str:
    """
    Convert repo/image names to Kubernetes-safe names
    """
    name = name.lower()
    name = re.sub(r"[^a-z0-9-]", "-", name)   # replace _ and others
    name = re.sub(r"-+", "-", name)           # collapse ---
    return name.strip("-")

def write_yaml(obj: dict) -> str:
    return yaml.safe_dump(obj, sort_keys=False)
