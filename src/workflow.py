#################################
# PRReviewWorkflow
#################################
import json
from typing import Annotated, TypedDict, List
from langgraph.graph import StateGraph, END
from .mcp_client import GitHubMCPClient
from .analyzer import PRAnalyzer
from .config import config

print("="*40)
# Workflow Orchestration
print("="*40)

class WorkflowState(TypedDict):
    """Represents the state of the PR review workflow."""
    pr_number: int
    pr_data: dict
    diff: str
    analysis_report: str
    comments: List[dict]
    approved: bool
    error: str

class ReviewWorkflow:
    """Orchestrates the PR review process using LangGraph."""

    def __init__(self):
        """Initializes the workflow components and the graph."""
        self.mcp = GitHubMCPClient()
        self.analyzer = PRAnalyzer()
        self.workflow = StateGraph(WorkflowState)
        self._build_graph()

    def _build_graph(self):
        """Defines nodes and edges of the workflow."""
        self.workflow.add_node("fetch_pr", self.fetch_pr)
        self.workflow.add_node("validate_branch", self.validate_branch)
        self.workflow.add_node("fetch_diff", self.fetch_diff)
        self.workflow.add_node("analyze", self.analyze)
        self.workflow.add_node("await_approval", self.await_approval)
        self.workflow.add_node("post_results", self.post_results)

        self.workflow.set_entry_point("fetch_pr")
        self.workflow.add_edge("fetch_pr", "validate_branch")
        self.workflow.add_edge("validate_branch", "fetch_diff")
        self.workflow.add_edge("fetch_diff", "analyze")
        self.workflow.add_edge("analyze", "await_approval")
        
        # Conditional edge for approval
        self.workflow.add_conditional_edges(
            "await_approval",
            lambda x: "post_results" if x.get("approved") else END
        )
        self.workflow.add_edge("post_results", END)

        self.app = self.workflow.compile()

    async def fetch_pr(self, state: WorkflowState):
        """Node: Fetch PR metadata."""
        print("#===============[ node: fetch_pr ]==========")
        try:
            result = await self.mcp.get_pr(state["pr_number"])
            return {"pr_data": result.content[0].text if hasattr(result, 'content') else result}
        except Exception as e:
            return {"error": f"Failed to fetch PR: {str(e)}"}

    async def validate_branch(self, state: WorkflowState):
        """Node: Validate target branch is main."""
        print("#===============[ node: validate_branch ]==========")
        pr_data = state.get("pr_data")
        if not pr_data:
            return {"error": "PR data missing in state"}
            
        if isinstance(pr_data, str):
            try:
                pr_data = json.loads(pr_data)
            except json.JSONDecodeError:
                pass # Already a dict or plain text
        
        if not isinstance(pr_data, dict):
            return {"error": f"Invalid PR data format: {type(pr_data)}"}

        target_branch = pr_data.get("base", {}).get("ref")
        if target_branch != "main":
            return {"error": f"PR targets '{target_branch}', but only 'main' is supported."}
        return {}

    async def fetch_diff(self, state: WorkflowState):
        """Node: Fetch PR diff."""
        print("#===============[ node: fetch_diff ]==========")
        try:
            diff_text = await self.mcp.get_diff(state["pr_number"])
            if diff_text.startswith("Error:"):
                return {"error": diff_text}
            return {"diff": diff_text}
        except Exception as e:
            return {"error": f"Failed to fetch diff: {str(e)}"}

    async def analyze(self, state: WorkflowState):
        """Node: Analyze changes using Ollama."""
        print("#===============[ node: analyze ]==========")
        diff = state.get("diff")
        if not diff:
            return {"error": "No diff found to analyze."}
            
        report = self.analyzer.analyze_diff(diff)
        comments = self.analyzer.generate_comments(diff)
        return {"analysis_report": report, "comments": comments}

    async def await_approval(self, state: WorkflowState):
        """Node: Wait for human approval (effectively a placeholder for UI)."""
        print("#===============[ node: await_approval ]==========")
        # This will be handled by the Streamlit layer setting state["approved"]
        return {}

    async def post_results(self, state: WorkflowState):
        """Node: Post comments and review to GitHub."""
        print("#===============[ node: post_results ]==========")
        pr_number = state["pr_number"]
        
        # Post inline comments
        for comment in state["comments"]:
            try:
                await self.mcp.create_review_comment(
                    pr_number, 
                    state["pr_data"].get("head", {}).get("sha"),
                    comment["path"],
                    comment["line"],
                    comment["body"]
                )
            except Exception as e:
                print(f"Error posting comment: {e}")

        # Post summary review
        await self.mcp.submit_review(pr_number, state["analysis_report"], "COMMENT")
        return {}

print("#===============[ Workflow implemented ]==========")
