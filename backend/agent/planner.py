import json
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

import os
api_key = os.getenv("GEMINI_API_KEY")
if not api_key or api_key == "your_gemini_api_key_here":
    client = None
    print("Warning: No valid GEMINI_API_KEY found, using fallback planner.")
else:
    try:
        client = genai.Client()
    except Exception:
        client = None

class StepPlan(BaseModel):
    step_id: str = Field(..., description="Unique identifier for this step, e.g., 'step_1'")
    tool_name: str = Field(..., description="The name of the registered tool to use")
    input_params_json: str = Field(..., description="Input parameters for the tool as a JSON-encoded string. May contain ${step_id.field} references")
    depends_on: List[str] = Field(default_factory=list, description="List of step_ids this step depends on")
    expected_output_type: str = Field(..., description="Description of the expected output")

class TaskGraph(BaseModel):
    steps: List[StepPlan] = Field(..., description="List of ordered execution steps")

def generate_plan(intent_goal: str, available_tools: List[str]) -> TaskGraph:
    if not client:
        # Fallback for dev
        return TaskGraph(
            steps=[
                StepPlan(
                    step_id="step_1",
                    tool_name="dummy_tool",
                    input_params_json=json.dumps({"task": intent_goal}),
                    depends_on=[],
                    expected_output_type="string"
                )
            ]
        )

    tools_str = ", ".join(available_tools)
    prompt = f"""
    You are an AI task planner. Break the user's intent down into a directed acyclic graph (DAG) of steps.
    You can only use the following registered tools: [{tools_str}].

    User's Goal: {intent_goal}

    Rules:
    1. Steps must be atomic.
    2. Use `depends_on` to express dependencies between steps. Independent steps can run in parallel.
    3. Maximum 15 steps.
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash', # Using flash to avoid quota limits on pro
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TaskGraph,
            temperature=0.1,
        ),
    )

    return TaskGraph.model_validate_json(response.text)

if __name__ == "__main__":
    plan = generate_plan("Fetch latest github issues and send a summary to slack", ["github_api", "slack_api"])
    print(plan.model_dump_json(indent=2))
