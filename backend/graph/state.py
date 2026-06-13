from typing import TypedDict, List, Dict, Any, Optional


class BRDState(TypedDict):
    # Core inputs/outputs
    raw_input: str
    cleaned_input: str
    questions: List[str]
    answers: List[str]
    brd_draft: str
    final_brd: str
    language: str
    localized_brd: str

    # Metadata & Tracking
    request_id: str
    project_name: str
    db_id: Optional[int]

    # Intermediate Artifacts (explainable AI / shared memory)
    context_analysis: str
    extracted_requirements: str
    stakeholder_analysis: str
    ambiguities_analysis: str
    risks_analysis: str
    structured_outline: str
    qa_review: str

    # Execution Logs / Traces
    agent_traces: List[Dict[str, Any]]
