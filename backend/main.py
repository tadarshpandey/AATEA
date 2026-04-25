from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

app = FastAPI(title="AATEA Backend", version="1.0.0")

# Allow CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskRequest(BaseModel):
    intent: str

@app.get("/")
def read_root():
    return {"message": "AATEA Backend is running"}

from agent.parser import parse_intent
from agent.planner import generate_plan, TaskGraph
from agent.executor import Executor, registry

# Global queue for websocket logs
import uuid
connected_clients = {}

async def broadcast_log(message: dict):
    for client_id, ws in connected_clients.items():
        try:
            await ws.send_json(message)
        except Exception:
            pass

class ExecuteRequest(BaseModel):
    intent: str
    plan: dict # The approved DAG

@app.post("/api/task/plan")
async def plan_task(request: TaskRequest):
    # 1. Parse Intent
    intent = parse_intent(request.intent)
    if not intent.is_valid:
        return {"status": "error", "message": "Invalid intent", "clarification": intent.clarifying_question}
    
    # 2. Plan
    available_tools = registry.list_tools()
    plan = generate_plan(intent.primary_goal, available_tools)
    
    return {"status": "success", "intent": intent.primary_goal, "plan": plan.model_dump()}

@app.post("/api/task/execute")
async def execute_task(request: ExecuteRequest):
    # 3. Execute an approved plan
    plan_obj = TaskGraph.model_validate(request.plan)
    executor = Executor(plan_obj, log_callback=broadcast_log)
    try:
        results = await executor.execute()
        return {"status": "success", "results": results}
    except Exception as e:
        return {"status": "failed", "error": str(e)}

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = str(uuid.uuid4())
    connected_clients[client_id] = websocket
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        del connected_clients[client_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
