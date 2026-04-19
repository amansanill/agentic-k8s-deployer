from shared.logger import log

def validate_intent(intent: dict) -> dict:
    log("Validator", "Validating intent")

    if "app_name" not in intent:
        log("Validator", "app_name missing, defaulting to 'app'")
        intent["app_name"] = "app"

    if "port" not in intent:
        log("Validator", "port missing, defaulting to 3000")
        intent["port"] = 3000

    intent["port"] = int(intent["port"])

    log("Validator", f"Validated intent: {intent}")
    return intent
