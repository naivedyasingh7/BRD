import json
from backend.graph.state import BRDState
from backend.services.sarvam import sarvam_service

# Helper function placeholder to keep imports/signatures clean if needed
def load_prompt(filename: str) -> str:
    """
    Placeholder prompt loader.
    TODO: Prompt engineer to put prompt template loading logic here.
    """
    return f"[Prompt Template Placeholder for {filename}]"

# 1. Input Agent
def input_agent(state: BRDState) -> dict:
    print("--- [Agent] Input Agent running ---")
    raw_input = state.get("raw_input", "").strip()
    language = state.get("language", "English")

    # Call mock translation/speech-to-text service
    if raw_input.lower().endswith((".wav", ".mp3", ".m4a", ".ogg", ".webm")):
        print(f"Processing audio input: {raw_input}")
        cleaned_input = sarvam_service.speech_to_text_translate(raw_input)
    else:
        print(f"Processing text input. Language: {language}")
        if language != "English" and raw_input:
            cleaned_input = sarvam_service.translate(raw_input, source_lang=language, target_lang="English")
        else:
            cleaned_input = raw_input

    print(f"Cleaned Input (English): {cleaned_input}")
    return {"cleaned_input": cleaned_input}

# 2. Extract Agent
def extract_agent(state: BRDState) -> dict:
    print("--- [Agent] Extract Agent running ---")
    
    # TODO: Implement real requirement extraction logic using LLM
    # Mocking structured data output
    mock_structured_data = {
        "problem": "Local retail shopkeepers face difficulty maintaining sales logs and billing during low/no internet scenarios.",
        "users": ["Shopkeeper", "Billing Staff", "Customer"],
        "features": [
            "Offline inventory management and product entry",
            "Offline digital invoice generation and billing module",
            "Automatic data sync when active internet is restored",
            "Multi-language digital receipts"
        ],
        "constraints": [
            "Low internet bandwidth",
            "Offline-first local database requirement",
            "Must run on basic Android smartphones or low-spec web client"
        ]
    }
    
    print(f"Extracted Requirements (Mocked): {mock_structured_data}")
    return {"structured_data": mock_structured_data}

# 3. Clarification Agent
def clarify_agent(state: BRDState) -> dict:
    print("--- [Agent] Clarification Agent running ---")
    questions = state.get("questions", [])
    answers = state.get("answers", [])

    # If questions have already been generated and we are receiving answers, do not generate new questions.
    if questions and len(answers) >= len(questions):
        print("Questions already answered. Skipping clarification.")
        return {}

    # TODO: Implement LLM ambiguity analyzer to generate smart questions
    # Mocking clarification questions
    mock_questions = [
        "Should this system run as a Mobile App, a Web App, or both?",
        "Do you need automated inventory deduction when billing occurs?"
    ]

    print(f"Generated clarification questions (Mocked): {mock_questions}")
    return {"questions": mock_questions}

# 4. BRD Generator Agent
def brd_agent(state: BRDState) -> dict:
    print("--- [Agent] BRD Generator Agent running ---")
    structured_data = state.get("structured_data", {})
    questions = state.get("questions", [])
    answers = state.get("answers", [])
    
    # Format QA pairs
    qa_pairs = []
    for q, a in zip(questions, answers):
        qa_pairs.append(f"Q: {q}\nA: {a}")
    clarification_qa = "\n\n".join(qa_pairs) if qa_pairs else "No clarification questions were answered."

    # TODO: Implement LLM BRD content creator using standard templates
    mock_draft = f"""# Business Requirements Document (BRD) - Retail Billing System (Mock)

## 1. Executive Summary
This document outlines requirements for a resilient Retail Billing System built for local shopkeepers to conduct uninterrupted sales operations offline.

## 2. Problem Statement & Objectives
Internet connectivity issues slow down store checkouts. This offline-first solution aims to prevent checkout delays and automate sales logging.

## 3. Scope of Work
- **In Scope**: Products listing, cart, offline checkout, and synchronization.
- **Out of Scope**: Direct card terminals connection (requires active API).

## 4. User Personas / Actors
- **Shopkeeper**: Owner with full access.
- **Billing Staff**: Basic cashier access.

## 5. Functional Requirements
- **Offline DB**: Read/write locally.
- **Auto-Sync**: Synchronize local state to remote DB when online.

## 6. Non-Functional Requirements
- **Availability**: High offline availability.
- **Localization**: Supports translation.

## 7. Clarifications Log
{clarification_qa}
"""
    print("BRD Draft generated (Mocked).")
    return {"brd_draft": mock_draft}

# 5. QA Agent
def qa_agent(state: BRDState) -> dict:
    print("--- [Agent] Quality Check Agent running ---")
    brd_draft = state.get("brd_draft", "")
    
    # TODO: Implement LLM quality checker / validator
    mock_final_brd = brd_draft + "\n\n---\n*Approved by QA Auditor [MOCK_VERIFICATION]*"
    
    print("Final BRD polished and approved by QA (Mocked).")
    return {"final_brd": mock_final_brd}

# 6. Localization Agent
def localize_agent(state: BRDState) -> dict:
    print("--- [Agent] Localization Agent running ---")
    final_brd = state.get("final_brd", "")
    language = state.get("language", "English")
    
    if language == "English":
        print("Target language is English. No translation needed.")
        return {"localized_brd": final_brd}
        
    print(f"Translating final BRD to {language} (Mocked)...")
    # Translate the final BRD using target mock service
    localized_brd = sarvam_service.translate(
        text=final_brd, 
        source_lang="English", 
        target_lang=language
    )
    
    print(f"BRD localized to {language} successfully (Mocked).")
    return {"localized_brd": localized_brd}
