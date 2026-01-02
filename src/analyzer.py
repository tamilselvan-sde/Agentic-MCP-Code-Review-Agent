#################################
# PRAnalyzer
#################################
import json
from langchain_ollama import OllamaLLM
from .config import config

print("="*40)
# Analysis Logic
print("="*40)

class PRAnalyzer:
    """Agentic analyzer using Ollama to review code changes."""

    def __init__(self):
        """Initializes the Ollama LLM."""
        self.llm = OllamaLLM(
            base_url=config.ollama_host,
            model=config.ollama_model
        )

    def analyze_diff(self, diff: str) -> str:
        """Analyzes a code diff and returns a structured report."""
        prompt = f"""
        You are an expert Senior Software Engineer and Security Researcher.
        Review the following Pull Request diff for:
        1. Bugs and logical errors.
        2. Security flaws (SQL injection, XSS, etc.).
        3. Performance risks.
        4. Design improvements and maintainability.
        5. Edge cases.

        Diff:
        {diff}

        Provide a structured report in Markdown format. 
        For specific issues, point out the file and logic if possible.
        """
        print("#===============[ LLM Analyzing Changes ]==========")
        return self.llm.invoke(prompt)

    def generate_comments(self, diff: str) -> list:
        """Generates specific inline comments for the diff."""
        prompt = f"""
        You are an expert code reviewer. Based on the diff below, generate a JSON list of comments.
        Each comment MUST have:
        - "path": the file path
        - "line": the line number in the diff (estimated)
        - "body": the comment content

        Diff:
        {diff}

        Return ONLY the JSON list.
        """
        print("#===============[ LLM Generating Comments ]==========")
        response = self.llm.invoke(prompt)
        try:
            # Simple extraction if block-quoted
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            return json.loads(response)
        except Exception as e:
            print(f"Error parsing comments: {e}")
            return []

print("#===============[ Analyzer implemented ]==========")
