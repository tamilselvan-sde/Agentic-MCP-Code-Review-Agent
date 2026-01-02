# Autonomous PR Review Agent

![App Interface](examples/Autonomous-PR-Review-Agent.png)

**Agentic-PR-Reviewer** is an autonomous, local-first AI system that automates Pull Request reviews. Orchestrated with **LangGraph** and powered by local LLMs via **Ollama**, it leverages the **GitHub Model Context Protocol (MCP)** to securely fetch diffs, analyze code, and post reviews—all without direct API key handling. Features a **Streamlit** UI for human-in-the-loop approval.

**Keywords:** `Autonomous Agent`, `AI Code Review`, `LangGraph`, `Ollama`, `GitHub MCP`, `Model Context Protocol`, `Local AI`, `Python`, `Streamlit`, `LLM Ops`

## Example Review
![GitHub Review](examples/Update-streamlit_app-py-by-tamilselvan-sde-·-Pull-Request-1-·-tamilselvan-sde-MCP-PostgreSQL.png)

## Workflow Diagram (Generated from Code)
![LangGraph Workflow](examples/workflow_diagram.png)

📖 **[View Detailed Workflow Documentation →](docs/WORKFLOW.md)**

## Features
- Fetches PR data and diffs via GitHub MCP.
- Validates target branch is `main`.
- Analyzes code changes for bugs, security, and performance using local Ollama (`gpt-oss:120b-cloud`).
- Human-in-the-loop approval via Streamlit UI.
- Posts inline comments and summary reviews to GitHub.

## Setup
1. **Ollama**: Ensure Ollama is running at `http://localhost:11434` with the model `gpt-oss:120b-cloud`.
2. **Environment Variables**: 
   - Copy `.env.example` to `.env`.
   - Add your `GITHUB_PERSONAL_ACCESS_TOKEN`.
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App
```bash
streamlit run app.py
```
