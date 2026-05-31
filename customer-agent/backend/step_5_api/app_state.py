from __future__ import annotations

from backend.step_5_api.workflow import CustomerServiceWorkflow

_workflow: CustomerServiceWorkflow | None = None


def init_workflow(workflow: CustomerServiceWorkflow) -> None:
    global _workflow
    _workflow = workflow


def get_workflow() -> CustomerServiceWorkflow:
    if _workflow is None:
        raise RuntimeError("Workflow not initialized. Call init_workflow() first.")
    return _workflow
