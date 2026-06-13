from typing import TypedDict, List, Dict, Any

class BRDState(TypedDict):
<<<<<<< Updated upstream
    raw_input: str            # Raw input path (audio) or raw text
    cleaned_input: str        # Translated and cleaned English text
    structured_data: Dict[str, Any] # Extracted requirements (problem, users, features, constraints)
    questions: List[str]      # List of clarification questions generated
    answers: List[str]        # List of answers to the clarification questions
    brd_draft: str            # Draft BRD generated
    final_brd: str            # Final, QA-approved BRD
    language: str             # Target language for localization (e.g., "Hindi", "Tamil")
    localized_brd: str        # Localized BRD in target language
=======
    raw_input: str
    cleaned_input: str
    questions: List[str]
    answers: List[str]
    brd_draft: str
    final_brd: str
    language: str
    localized_brd: str
    mermaid_flowchart: str
    request_id: str
    project_name: str
    db_id: Optional[int]
    context_analysis: str
    extracted_requirements: str
    stakeholder_analysis: str
    ambiguities_analysis: str
    risks_analysis: str
    structured_outline: str
    qa_review: str
    agent_traces: List[Dict[str, Any]]
>>>>>>> Stashed changes
