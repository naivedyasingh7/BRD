from typing import TypedDict, List, Dict, Any

class BRDState(TypedDict):
    raw_input: str
    cleaned_input: str
    structured_data: Dict[str, Any]
    questions: List[str]
    answers: List[str]
    brd_draft: str
    final_brd: str
    language: str
    localized_brd: str
