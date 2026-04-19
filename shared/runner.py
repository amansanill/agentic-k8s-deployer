import subprocess
from shared.logger import log

def run(cmd, source, cwd=None):
    log(source, f"Running: {' '.join(cmd)}")

    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    for line in process.stdout:
        log(source, line.rstrip())

    process.wait()

    if process.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
