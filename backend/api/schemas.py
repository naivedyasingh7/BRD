from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ClarifyRequest(BaseModel):
    state: Dict[str, Any] = Field(..., description="The complete serialized state dictionary from LangGraph")
    answers: List[str] = Field(..., description="List of answers supplied for the clarification questions")


class AgentTraceSchema(BaseModel):
    agent_role: str = Field(..., description="Role name of the agent (e.g. Context Analyst)")
    step_name: str = Field(..., description="Name of the node execution step")
    status: str = Field(..., description="Success, Failure, etc.")
    start_time: str = Field(..., description="Timestamp when the agent started")
    end_time: str = Field(..., description="Timestamp when the agent ended")
    duration_seconds: float = Field(..., description="Time taken by the agent to run in seconds")
    output_summary: str = Field(..., description="Short summary of the agent's output")


class BRDStateResponse(BaseModel):
    raw_input: str
    cleaned_input: str
    structured_data: Dict[str, Any]
    questions: List[str]
    answers: List[str]
    brd_draft: str
    final_brd: str
    language: str
    localized_brd: str
    db_id: Optional[int] = None
    request_id: Optional[str] = None
    agent_traces: Optional[List[AgentTraceSchema]] = None


class ProjectHistoryResponse(BaseModel):
    id: int
    project_name: str
    language: str
    created_at: str


class BRDDetailResponse(BaseModel):
    id: int
    project_name: str
    version: str
    raw_input: Optional[str]
    cleaned_input: Optional[str]
    english_brd: Optional[str]
    localized_brd: Optional[str]
    language: str
    created_at: str
    agent_traces: Optional[List[Dict[str, Any]]] = None
