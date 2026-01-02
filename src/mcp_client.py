#################################
# GitHubMCPClient
#################################
import asyncio
import json
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from .config import config

print("="*40)
# MCP Client Logic
print("="*40)

class GitHubMCPClient:
    """Client for interacting with GitHub via the MCP server."""

    def __init__(self):
        """Initializes the MCP client parameters."""
        self.server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-github"],
            env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": config.github_token}
        )

    async def _call_tool(self, tool_name: str, arguments: dict):
        """Helper to call a specific MCP tool."""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                return result

    async def get_pr(self, pr_number: int):
        """Fetches PR details from GitHub."""
        return await self._call_tool("get_pull_request", {
            "owner": config.repo_owner,
            "repo": config.repo_name,
            "pull_number": pr_number
        })

    async def get_diff(self, pr_number: int):
        """Fetches PR files and reconstructs the diff from patches."""
        print("#===============[ MCP: Fetching PR Files for Diff ]==========")
        result = await self._call_tool("get_pull_request_files", {
            "owner": config.repo_owner,
            "repo": config.repo_name,
            "pull_number": pr_number
        })
        
        # Parse the JSON response from the tool
        # The MCP tool returns a list of file objects in its content[0].text
        try:
            if hasattr(result, 'content'):
                files_data = json.loads(result.content[0].text)
            else:
                files_data = result # Fallback if already parsed
                
            full_diff = ""
            for file in files_data:
                filename = file.get("filename", "unknown")
                patch = file.get("patch", "")
                if patch:
                    full_diff += f"File: {filename}\n{patch}\n\n"
            
            return full_diff
        except Exception as e:
            print(f"Error reconstructing diff: {e}")
            return f"Error: Failed to reconstruct diff from files. {str(e)}"

    async def create_review_comment(self, pr_number: int, commit_id: str, path: str, line: int, body: str):
        """Adds a review comment to a specific line."""
        return await self._call_tool("create_pull_request_review_comment", {
            "owner": config.repo_owner,
            "repo": config.repo_name,
            "pull_number": pr_number,
            "commit_id": commit_id,
            "path": path,
            "line": line,
            "body": body
        })

    async def submit_review(self, pr_number: int, body: str, event: str = "COMMENT"):
        """Submits the final summary review."""
        return await self._call_tool("create_pull_request_review", {
            "owner": config.repo_owner,
            "repo": config.repo_name,
            "pull_number": pr_number,
            "body": body,
            "event": event
        })

print("#===============[ MCP Client implemented ]==========")
