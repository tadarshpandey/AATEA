import os
from pydantic import BaseModel, Field
from typing import List, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# We initialize the client globally for the parser
api_key = os.getenv("GEMINI_API_KEY")
if not api_key or api_key == "your_gemini_api_key_here":
    client = None
    print("Warning: No valid GEMINI_API_KEY found, using fallback parser.")
else:
    try:
        client = genai.Client()
    except Exception as e:
        client = None
        print(f"Warning: Gemini client initialization failed: {e}")

class TaskIntent(BaseModel):
    confidence_score: float = Field(..., description="Score between 0.0 and 1.0 indicating confidence in understanding the user's intent")
    primary_goal: str = Field(..., description="A short summary of the main objective")
    clarifying_question: Optional[str] = Field(None, description="If confidence is < 0.7, a single question to ask the user")
    is_valid: bool = Field(..., description="True if the request makes sense as a task, False otherwise")

def parse_intent(user_instruction: str) -> TaskIntent:
    if not client:
        # Fallback for development without an API key
        return TaskIntent(
            confidence_score=0.9,
            primary_goal="Fallback parsed goal: " + user_instruction,
            clarifying_question=None,
            is_valid=True
        )

    prompt = f"""
    You are an intelligent task parser. Your job is to analyze the user's natural language instruction
    and determine the core intent. If the instruction is vague, set the confidence score low (< 0.7)
    and provide a clarifying question.

    User Instruction:
    {user_instruction}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TaskIntent,
            temperature=0.1,
        ),
    )
    
    # Parse the returned JSON directly into our Pydantic model
    return TaskIntent.model_validate_json(response.text)

if __name__ == "__main__":
    # Quick test
    intent = parse_intent("Fetch the latest logs from github")
    print(intent.model_dump_json(indent=2))
