from typing import TypedDict, List, Dict, Any

class BRDState(TypedDict):
    raw_input: str            # Raw input path (audio) or raw text
    cleaned_input: str        # Translated and cleaned English text
    structured_data: Dict[str, Any] # Extracted requirements (problem, users, features, constraints)
    questions: List[str]      # List of clarification questions generated
    answers: List[str]        # List of answers to the clarification questions
    brd_draft: str            # Draft BRD generated
    final_brd: str            # Final, QA-approved BRD
    language: str             # Target language for localization (e.g., "Hindi", "Tamil")
    localized_brd: str        # Localized BRD in target language
