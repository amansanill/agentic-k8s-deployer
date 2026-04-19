from flask import Flask, render_template, request, Response
import subprocess
import sys
import os

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/deploy")
def deploy():
    repo = request.args.get("repo")

    print("[WEB] Deploy request received:", repo)

    def generate():
        print("[WEB] Starting pipeline subprocess")

        cmd = [sys.executable, "../main.py"]
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        process.stdin.write(repo + "\n")
        process.stdin.flush()
        process.stdin.close()

        for line in process.stdout:
            print("[PIPELINE]", line.strip())
            yield line + "<br>"

        process.wait()
        print("[WEB] Pipeline finished")

    return Response(generate(), mimetype="text/html")

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
