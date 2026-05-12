from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.agent_config_service import (
    get_agent_config,
    list_agent_configs,
    reset_agent_config,
    update_agent_config,
)

router = APIRouter(prefix="/agents", tags=["Agent Config"])


class AgentUpdateRequest(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    features: Optional[list[str]] = None
    prompt: Optional[str] = Field(default=None, min_length=1)


@router.get("/config")
def get_agents_config():
    return {"agents": list_agent_configs()}


@router.get("/config/{agent_id}")
def get_one_agent_config(agent_id: str):
    try:
        return get_agent_config(agent_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.put("/config/{agent_id}")
def update_one_agent_config(agent_id: str, req: AgentUpdateRequest):
    try:
        payload: Dict[str, Any] = req.model_dump(exclude_none=True)
    except AttributeError:
        payload = req.dict(exclude_none=True)
    try:
        return update_agent_config(agent_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/config/{agent_id}/reset")
def reset_one_agent_config(agent_id: str):
    try:
        return reset_agent_config(agent_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/config/reset")
def reset_all_agent_config():
    return {"agents": reset_agent_config()}
