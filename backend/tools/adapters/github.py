import httpx
from typing import Dict, Any
import os

async def fetch_github_issues(params: Dict[str, Any]) -> str:
    """
    Fetches issues from a public github repository.
    Expected params: 
    - 'owner': str (e.g. 'facebook')
    - 'repo': str (e.g. 'react')
    - 'limit': int (optional, default 5)
    """
    owner = params.get('owner', 'facebook')
    repo = params.get('repo', 'react')
    limit = int(params.get('limit', 5))
    
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    
    async with httpx.AsyncClient() as client:
        # Public unauthenticated request
        response = await client.get(url, params={"per_page": limit, "state": "open"})
        
        if response.status_code != 200:
            raise Exception(f"GitHub API Error {response.status_code}: {response.text}")
            
        issues = response.json()
        
        if not issues:
            return f"No open issues found in {owner}/{repo}"
            
        summary = f"Found {len(issues)} open issues in {owner}/{repo}:\n"
        for i, issue in enumerate(issues):
            summary += f"{i+1}. [{issue['state']}] {issue['title']} (URL: {issue['html_url']})\n"
            
        return summary
