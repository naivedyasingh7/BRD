from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ClarifyRequest(BaseModel):
    state: Dict[str, Any] = Field(..., description="The complete serialized state dictionary from LangGraph")
    answers: List[str] = Field(..., description="List of answers supplied for the clarification questions")


class ChatRequest(BaseModel):
    brd_id: int = Field(..., description="The ID of the BRD to query")
    question: str = Field(..., description="The question the user is asking about the transcript")

class ChatResponse(BaseModel):
    answer: str


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
    questions: List[str]
    answers: List[str]
    brd_draft: str
    final_brd: str
    language: str
    localized_brd: str
    mermaid_flowchart: Optional[str] = None
    db_id: Optional[int] = None
    request_id: Optional[str] = None
    project_name: Optional[str] = None
    context_analysis: Optional[str] = None
    extracted_requirements: Optional[str] = None
    stakeholder_analysis: Optional[str] = None
    ambiguities_analysis: Optional[str] = None
    risks_analysis: Optional[str] = None
    structured_outline: Optional[str] = None
    qa_review: Optional[str] = None
    agent_traces: Optional[List[AgentTraceSchema]] = None
    structured_data: Optional[Dict[str, Any]] = None


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
    mermaid_flowchart: Optional[str] = None
    created_at: str
    agent_traces: Optional[List[Dict[str, Any]]] = None
