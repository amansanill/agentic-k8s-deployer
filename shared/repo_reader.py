import tempfile
import os
from shared.runner import run
from shared.logger import log

def clone_repo(repo_url: str) -> str:
    log("RepoReader", "Creating temporary directory")
    temp_dir = tempfile.mkdtemp()

    log("RepoReader", f"Cloning repository: {repo_url}")
    run(
        ["git", "clone", repo_url, temp_dir],
        source="RepoReader"
    )

    log("RepoReader", f"Repository cloned to {temp_dir}")
    return temp_dir
