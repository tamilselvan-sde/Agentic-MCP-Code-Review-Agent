#################################
# PRReviewApp
#################################
import streamlit as st
import asyncio
from src.workflow import ReviewWorkflow
from src.config import config

st.set_page_config(page_title="Autonomous PR Review Agent", layout="wide")

print("="*40)
# UI Layer
print("="*40)

def run_async(coro):
    """Helper to run async code in Streamlit."""
    return asyncio.run(coro)

st.title("🧠 Autonomous PR Review Agent")
st.markdown("Automate your PR reviews with LangGraph and Ollama.")

if "workflow_state" not in st.session_state:
    st.session_state.workflow_state = None

pr_number = st.number_input("Enter Pull Request Number", min_value=1, step=1)

if st.button("Start Analysis"):
    with st.spinner("Fetching PR and Analyzing..."):
        workflow = ReviewWorkflow()
        initial_state = {"pr_number": pr_number, "approved": False}
        
        # Run workflow up to await_approval
        # Note: In a real production app, we'd use LangGraph's checkpointing.
        # For this local demo, we simulate it by running nodes sequentially or using a flag.
        try:
            # We'll run the workflow manually for this demo to show intermediate state
            state = initial_state
            
            # Step 1: Fetch PR
            state.update(run_async(workflow.fetch_pr(state)))
            if "error" in state: raise Exception(state["error"])
            
            # Step 2: Validate Branch
            validation_result = run_async(workflow.validate_branch(state))
            if "error" in validation_result: raise Exception(validation_result["error"])
            state.update(validation_result)
            
            # Step 3: Fetch Diff
            state.update(run_async(workflow.fetch_diff(state)))
            if "error" in state: raise Exception(state["error"])
            
            # Step 4: Analyze
            state.update(run_async(workflow.analyze(state)))
            if "error" in state: raise Exception(state["error"])
            
            st.session_state.workflow_state = state
        except Exception as e:
            st.error(f"Error: {e}")

if st.session_state.workflow_state:
    state = st.session_state.workflow_state
    
    st.subheader("Analysis Report")
    st.markdown(state["analysis_report"])
    
    st.subheader("Proposed Comments")
    for cmd in state["comments"]:
        st.info(f"**File:** {cmd['path']} (Line {cmd['line']})\n\n{cmd['body']}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve & Post"):
            with st.spinner("Posting to GitHub..."):
                state["approved"] = True
                workflow = ReviewWorkflow()
                run_async(workflow.post_results(state))
                st.success("Review posted successfully!")
                st.session_state.workflow_state = None
    with col2:
        if st.button("❌ Reject"):
            st.warning("Review rejected. Nothing posted.")
            st.session_state.workflow_state = None

print("#===============[ UI Layer implemented ]==========")
