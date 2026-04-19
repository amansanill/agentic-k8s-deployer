from shared.logger import log


def validate_intent(intent: dict, context: dict) -> dict:
    log("Validator", "Validating intent")

    # ---------------- DEFAULTS ----------------
    intent.setdefault("app_name", "")
    intent.setdefault("port", 80)
    intent.setdefault("image", "")
    intent.setdefault("db_detected", False)

    # ---------------- TYPE SAFETY ----------------
    try:
        intent["port"] = int(intent["port"])
    except:
        log("Validator", "Invalid port → defaulting to 80")
        intent["port"] = 80

    # ---------------- APP NAME FIX ----------------
    if not intent["app_name"]:
        intent["app_name"] = context.get("repo_name", "app")

    # ---------------- IMAGE FIX ----------------
    if not intent["image"]:
        log("Validator", "Image missing → using app_name as image")
        intent["image"] = intent["app_name"]

    # ---------------- SOURCE OF TRUTH ----------------
    intent["has_dockerfile"] = context.get("has_dockerfile", False)
    intent["has_compose"] = context.get("has_compose", False)

    # ---------------- DB DETECTION ----------------
    intent["db_detected"] = (
        intent.get("db_detected", False)
        or context.get("has_sql_file", False)
    )

    # ---------------- PORT FROM CONTEXT (BEST PRACTICE) ----------------
    if context.get("container_port"):
        log("Validator", f"Using container port from compose: {context['container_port']}")
        intent["port"] = context["container_port"]

    # ---------------- BUILD DECISION ----------------
    intent["build_required"] = intent["has_dockerfile"]

    log("Validator", f"Final validated intent: {intent}")
    return intent
