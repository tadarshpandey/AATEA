import httpx
from typing import Dict, Any
import os
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env')
load_dotenv(dotenv_path=env_path, override=True)

async def send_slack_message(params: Dict[str, Any]) -> str:
    """
    Sends a message via a predefined Slack Webhook URL.
    Expected params:
    - 'message': str
    """
    message = params.get('message', 'No message provided.')
    webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    if webhook_url:
        webhook_url = webhook_url.strip()
        
    if not webhook_url or webhook_url == "your_slack_webhook_here":
        # Simulate success for testing if no real webhook is provided
        return f"[Simulated Slack Send] Message: {message[:50]}..."
        
    async with httpx.AsyncClient(follow_redirects=True) as client:
        print(f"[DEBUG] Sending to Slack Webhook URL: {webhook_url}")
        print(f"[DEBUG] Message payload: {message[:100]}")
        response = await client.post(webhook_url, json={"text": message})
        print(f"[DEBUG] Response status: {response.status_code}")
        
        if response.status_code != 200:
            raise Exception(f"Slack Webhook Error {response.status_code}: {response.text}")
            
        return "Message successfully sent to Slack."
