from datetime import datetime
import sys

def log(source: str, message: str):
    """
    Central logging function for the entire pipeline
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] [{source}] {message}"

    print(line)
    sys.stdout.flush()
