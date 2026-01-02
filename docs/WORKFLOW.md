# Workflow Architecture

This document provides a comprehensive overview of the **Agentic-PR-Reviewer** workflow architecture, orchestrated using **LangGraph**.

## Workflow Diagram

![LangGraph Workflow](examples/workflow_diagram.png)

*This diagram is automatically generated from the code using `graph.get_graph().draw_mermaid_png()`*

---

## Architecture Overview

The system is built on a **state machine** pattern where each node performs a specific operation and transitions to the next node based on the workflow graph. The entire orchestration is handled by LangGraph, ensuring robust error handling and state management.

### State Schema

```python
class WorkflowState(TypedDict):
    pr_number: int           # Input PR number
    pr_data: dict           # Full PR metadata from GitHub
    diff: str               # Reconstructed code diff
    analysis_report: str    # LLM-generated analysis
    comments: List[dict]    # Inline review comments
    approved: bool          # Human approval flag
    error: str              # Error message if any
```

---

## Workflow Nodes

### 1. **Fetch PR Data**
- **Purpose**: Retrieves Pull Request metadata from GitHub.
- **Input**: `pr_number`
- **Output**: `pr_data` (JSON object containing PR title, description, author, branches, etc.)
- **MCP Tool**: `get_pull_request`
- **Error Handling**: Returns error state if PR not found or access denied.

---

### 2. **Validate Branch**
- **Purpose**: Ensures the PR targets the `main` branch (configurable constraint).
- **Input**: `pr_data`
- **Output**: Empty dict if valid, error state otherwise
- **Logic**: Parses `pr_data.base.ref` and compares to "main"
- **Why**: Enforces branch policy to prevent reviews on non-production PRs.

---

### 3. **Fetch Diffs**
- **Purpose**: Reconstructs the full code diff from individual file patches.
- **Input**: `pr_number`
- **Output**: `diff` (concatenated patch strings)
- **MCP Tool**: `get_pull_request_files` (iterates and joins `patch` fields)
- **Note**: `get_pull_request_diff` is not available in the MCP server, so we reconstruct manually.

---

### 4. **Analyze Changes**
- **Purpose**: Uses local Ollama LLM to perform deep code analysis.
- **Input**: `diff`
- **Output**: `analysis_report`, `comments`
- **LLM Model**: `gpt-oss:120b-cloud` (configurable)
- **Analysis Criteria**:
  - Bugs and logical errors
  - Security flaws (SQL injection, XSS, etc.)
  - Performance risks
  - Design improvements
  - Edge cases

---

### 5. **Await Human Approval**
- **Purpose**: Pauses the workflow for human review via Streamlit UI.
- **Input**: Full state with `analysis_report` and `comments`
- **Output**: Updated `approved` flag
- **Decision Point**: 
  - If `approved == true` → Proceed to **Post Results**
  - If `approved == false` → End workflow

---

### 6. **Post Results**
- **Purpose**: Posts inline comments and summary review to GitHub.
- **Input**: `comments`, `analysis_report`, `pr_data`
- **MCP Tools**:
  - `create_pull_request_review` (for summary)
  - Inline comment posting (per comment)
- **Output**: Success confirmation

---

## Data Flow

```
User Input (PR #)
     ↓
[Fetch PR Data] → pr_data
     ↓
[Validate Branch] → validation check
     ↓
[Fetch Diffs] → diff
     ↓
[Analyze Changes] → analysis_report, comments
     ↓
[Await Approval] → approved flag
     ↓ (if approved)
[Post Results] → GitHub API
     ↓
Done
```

---

## Error Handling Strategy

1. **Per-Node Errors**: Each node returns `{"error": "..."}` instead of raising exceptions.
2. **State Propagation**: Errors are carried in the state and checked by the Streamlit UI.
3. **Graceful Degradation**: If analysis fails, the user sees the error instead of a crash.

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Orchestration** | LangGraph | State machine workflow |
| **LLM** | Ollama (`gpt-oss:120b-cloud`) | Code analysis |
| **GitHub Integration** | MCP Server (stdio) | PR data & posting |
| **Frontend** | Streamlit | Human approval UI |
| **Language** | Python 3.12 | Implementation |

---

## How to Regenerate the Diagram

Run the following command to regenerate the workflow diagram from code:

```bash
export PYTHONPATH=$PYTHONPATH:.
python3 tests/generate_graph.py
```

This will update `examples/workflow_diagram.png` with the latest workflow structure.

---

## Future Enhancements

- [ ] Support for multiple target branches
- [ ] Integration with CI/CD pipelines
- [ ] Configurable analysis severity levels
- [ ] Automatic PR merge on approval
- [ ] Multi-LLM ensemble reviews
