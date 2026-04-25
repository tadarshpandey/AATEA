import asyncio
from typing import Dict, Any, Callable
import networkx as nx
from .planner import TaskGraph, StepPlan

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}

    def register(self, name: str, func: Callable):
        self._tools[name] = func

    def get(self, name: str) -> Callable:
        return self._tools.get(name)

    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

registry = ToolRegistry()

# Dummy tool for testing
async def dummy_tool(params: Dict[str, Any]) -> str:
    print(f"[DummyTool] Executing with params: {params}")
    import asyncio
    await asyncio.sleep(1)
    return f"Success: Processed {params}"

registry.register("dummy_tool", dummy_tool)

# Register new adapters
import sys
import os
sys.path.append(os.path.dirname(__file__))
from tools.adapters.github import fetch_github_issues
from tools.adapters.slack import send_slack_message

registry.register("github_api", fetch_github_issues)
registry.register("slack_webhook", send_slack_message)

import json
from tenacity import retry, wait_exponential, stop_after_attempt

class Executor:
    def __init__(self, graph: TaskGraph, log_callback=None):
        self.graph = graph
        self.dag = nx.DiGraph()
        self.step_outputs: Dict[str, Any] = {}
        self.log_callback = log_callback
        self._build_dag()

    async def _log(self, message: str, status: str = "info"):
        if self.log_callback:
            await self.log_callback({"message": message, "status": status})
        else:
            print(f"[{status.upper()}] {message}")

    def _build_dag(self):
        for step in self.graph.steps:
            self.dag.add_node(step.step_id, data=step)
            for dep in step.depends_on:
                self.dag.add_edge(dep, step.step_id)
        
        if not nx.is_directed_acyclic_graph(self.dag):
            raise ValueError("Task graph contains circular dependencies")

    def _resolve_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        resolved = {}
        for k, v in params.items():
            if isinstance(v, str) and v.startswith("${") and v.endswith("}"):
                ref = v[2:-1]
                step_id = ref.split(".")[0]
                resolved[k] = self.step_outputs.get(step_id, v)
            else:
                resolved[k] = v
        return resolved

    async def _execute_step(self, step_id: str):
        step_data: StepPlan = self.dag.nodes[step_id]['data']
        await self._log(f"Starting step [{step_id}] using tool '{step_data.tool_name}'", "running")
        
        tool_func = registry.get(step_data.tool_name)
        if not tool_func:
            err = f"Tool {step_data.tool_name} not found"
            await self._log(err, "error")
            raise ValueError(err)

        try:
            raw_params = json.loads(step_data.input_params_json)
        except Exception:
            raw_params = {}

        resolved_params = self._resolve_params(raw_params)
        
        # We define a sync wrapper or use tenacity's async retry if tool_func is async
        # Let's use an inline async function for tenacity
        @retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3), reraise=True)
        async def run_with_retry():
            return await tool_func(resolved_params)
            
        try:
            result = await run_with_retry()
            self.step_outputs[step_id] = result
            await self._log(f"Completed step [{step_id}] successfully", "success")
        except Exception as e:
            await self._log(f"Failed step [{step_id}] after retries: {str(e)}", "error")
            raise e

    async def execute(self):
        await self._log("Starting execution graph...", "info")
        for node in nx.topological_sort(self.dag):
            await self._execute_step(node)
        await self._log("Execution graph completed successfully.", "success")
        return self.step_outputs

if __name__ == "__main__":
    from .planner import StepPlan, TaskGraph
    tg = TaskGraph(
        steps=[
            StepPlan(step_id="1", tool_name="dummy_tool", input_params={"x": 10}, depends_on=[], expected_output_type="str"),
            StepPlan(step_id="2", tool_name="dummy_tool", input_params={"y": "${1.output}"}, depends_on=["1"], expected_output_type="str")
        ]
    )
    
    exec_engine = Executor(tg)
    asyncio.run(exec_engine.execute())
    print(exec_engine.step_outputs)
