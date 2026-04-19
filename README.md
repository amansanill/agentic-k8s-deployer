# 🚀 Agentic AI Kubernetes Deployer

An intelligent, agent-driven system that automates end-to-end Kubernetes deployments directly from a GitHub repository.

---

## 📌 Overview

This project uses an **Agentic AI architecture** to eliminate manual Kubernetes configuration by automatically:

* Cloning a GitHub repository
* Understanding application structure
* Generating deployment intent using LLMs
* Validating and correcting configurations using guardrails
* Building Docker images (if required)
* Deploying applications to Kubernetes
* Handling dynamic apps with database setup

---

## 🧠 Architecture

The system is built using three core agents:

### 🔹 Generator Agent

* Uses LLM (Gemma via Ollama)
* Converts repository context into deployment intent (JSON)

### 🔹 Validator Agent (Guardrails)

* Prevents hallucinations
* Enforces correctness using repository-derived context
* Fixes:

  * Missing fields
  * Incorrect ports (container vs host)
  * Database detection
* Ensures safe deployment decisions

### 🔹 Executor Agent

* Builds & pushes Docker images
* Generates Kubernetes YAMLs
* Deploys:

  * Application
  * Services
  * Database (MySQL if detected)
* Exposes application via NodePort

---

## ⚙️ Key Features

✅ Fully automated Kubernetes deployment
✅ Works with both **static and dynamic applications**
✅ Intelligent **database detection and setup**
✅ Context-aware **port correction (docker-compose parsing)**
✅ LLM + deterministic guardrails (hybrid AI system)
✅ Real-time deployment logs via web UI

---

## 🛡️ Guardrails (Core Strength)

This system implements **functional guardrails** to ensure reliability:

* Overrides LLM outputs using actual repository analysis
* Extracts container ports from docker-compose
* Prevents invalid deployments (e.g., missing images)
* Uses hybrid validation (LLM + deterministic logic)

---

## 🏗️ Project Structure

```
agentic-k8s-deployer/
│
├── generator_agent/
├── validator_agent/
├── executor_agent/
├── shared/
├── web/
├── main.py
└── requirements.txt
```

---

## 🚀 How It Works

1. User provides GitHub repo URL
2. Repo is cloned
3. Context is extracted (Dockerfile, compose, SQL, etc.)
4. Generator creates deployment intent
5. Validator enforces correctness (guardrails)
6. Executor deploys to Kubernetes

---

## 🌐 Example Output

```
🚀 Application is LIVE at:
http://<node-ip>:<node-port>
```

---

## 🔀 Branches

* `static` → Basic deployment (static apps only)
* `dynamic` → Advanced version with:

  * Database support
  * Guardrails
  * Context-aware deployment

---

## 🧪 Tech Stack

* Python
* Kubernetes (kubectl)
* Docker
* Flask (Web UI)
* Ollama (Gemma LLM)

---

## 🎯 Project Objective

> To develop an Agentic AI-based system that automates Kubernetes deployment using a GitHub repository link, reducing manual configuration effort by over 80% and deployment time by at least 60%.

---

## 🔮 Future Improvements

* Multi-service deployment (microservices)
* Persistent volumes for databases
* Config auto-detection (.env, config files)
* RBAC and security guardrails
* Helm chart generation

---

## 👨‍💻 Author

Aman Sanil
Cloud & DevOps Enthusiast

---

## ⭐ If you like this project

Give it a ⭐ on GitHub!
