import os
import json
import re
from backend.graph.state import BRDState
from backend.services.llm import llm_service
from backend.services.sarvam import sarvam_service

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_prompt(filename: str) -> str:
    path = os.path.join(PROJECT_ROOT, "prompts", filename)
    if not os.path.exists(path):
        # Fallback if file doesn't exist yet
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def parse_json_from_text(text: str) -> dict:
    """Helper to parse JSON from model responses containing markdown wrappers."""
    # Remove markdown code blocks if present
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    text = text.strip()
    
    # Extract only the JSON part using braces
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception as e:
            print(f"Error decoding extracted JSON substring: {e}")
            
    try:
        return json.loads(text)
    except Exception as e:
        print(f"Failed to parse JSON directly: {e}. Raw: {text}")
        return {
            "problem": text[:200],
            "users": ["User"],
            "features": ["Feature extraction failed, please check inputs"],
            "constraints": []
        }

# 1. Input Agent
def input_agent(state: BRDState) -> dict:
    print("--- [Agent] Input Agent running ---")
    raw_input = state.get("raw_input", "").strip()
    language = state.get("language", "English")

    # Check if input is a path to an audio file
    is_audio = any(raw_input.lower().endswith(ext) for ext in [".wav", ".mp3", ".m4a", ".ogg", ".webm"])

    if is_audio:
        print(f"Processing audio input: {raw_input}")
        cleaned_input = sarvam_service.speech_to_text_translate(raw_input)
    else:
        print(f"Processing text input. Language: {language}")
        if language != "English" and raw_input:
            # Translate regional text to English
            cleaned_input = sarvam_service.translate(raw_input, source_lang=language, target_lang="English")
        else:
            cleaned_input = raw_input

    print(f"Cleaned Input (English): {cleaned_input}")
    return {"cleaned_input": cleaned_input}

# 2. Extract Agent
def extract_agent(state: BRDState) -> dict:
    print("--- [Agent] Extract Agent running ---")
    cleaned_input = state.get("cleaned_input", "")
    
    prompt_template = load_prompt("extraction.txt")
    prompt = prompt_template.format(cleaned_input=cleaned_input)
    
    response = llm_service.generate(
        prompt=prompt,
        system_instruction="You are an expert Business Analyst. Extract details and return strictly formatted JSON."
    )
    
    structured_data = parse_json_from_text(response)
    print(f"Extracted Requirements: {structured_data}")
    return {"structured_data": structured_data}

# 3. Clarification Agent
def clarify_agent(state: BRDState) -> dict:
    print("--- [Agent] Clarification Agent running ---")
    structured_data = state.get("structured_data", {})
    cleaned_input = state.get("cleaned_input", "")
    questions = state.get("questions", [])
    answers = state.get("answers", [])

    # If questions have already been generated and we are receiving answers, do not generate new questions.
    if questions and len(answers) >= len(questions):
        print("Questions already answered. Skipping clarification.")
        return {}

    # Otherwise, analyze the requirements and generate 2-3 specific, short clarifying questions
    prompt = f"""
    Analyze the following requirements:
    Input Text: {cleaned_input}
    Extracted Structure: {json.dumps(structured_data, indent=2)}

    Identify the top 2-3 most critical ambiguities or missing details (e.g. mobile vs web, offline support, user login, integrations, payment gateways, budget/bandwidth limitations).
    Write 2 or 3 short, specific, and direct questions that the user can answer to clarify their needs.
    Format the output strictly as a JSON array of strings. Do not include markdown code block syntax.
    Example output format:
    [
      "Do you want this app to work offline, or will it require a continuous internet connection?",
      "Do you need a billing system with automated tax calculation (like GST in India)?"
    ]
    """
    
    response = llm_service.generate(
        prompt=prompt,
        system_instruction="You are a Product Owner assistant. Identify critical requirements gaps and output a JSON list of questions."
    )
    
    try:
        # Clean response if markdown blocks are returned
        clean_resp = re.sub(r"```json\s*", "", response)
        clean_resp = re.sub(r"```\s*", "", clean_resp).strip()
        match = re.search(r"\[.*\]", clean_resp, re.DOTALL)
        if match:
            questions_list = json.loads(match.group(0))
        else:
            questions_list = json.loads(clean_resp)
    except Exception as e:
        print(f"Failed to parse clarification questions: {e}. Raw: {response}")
        # Default questions if parsing fails
        questions_list = [
            "Should this be built as a Mobile App, a Web App, or both?",
            "Do you require user authentication/login for different staff roles?"
        ]

    print(f"Generated clarification questions: {questions_list}")
    return {"questions": questions_list}

# 4. BRD Generator Agent
def brd_agent(state: BRDState) -> dict:
    print("--- [Agent] BRD Generator Agent running ---")
    structured_data = state.get("structured_data", {})
    questions = state.get("questions", [])
    answers = state.get("answers", [])
    
    # Formulate a string of QA clarification pairs
    qa_pairs = []
    for q, a in zip(questions, answers):
        qa_pairs.append(f"Q: {q}\nA: {a}")
    clarification_qa = "\n\n".join(qa_pairs) if qa_pairs else "No clarification questions were asked."

    # Extract a name for the project
    project_name = structured_data.get("problem", "Software System").split(".")[0][:50]
    
    prompt_template = load_prompt("brd.txt")
    prompt = prompt_template.format(
        project_name=project_name,
        structured_data=json.dumps(structured_data, indent=2),
        clarification_qa=clarification_qa
    )
    
    brd_draft = llm_service.generate(
        prompt=prompt,
        system_instruction="You are a Principal Product Manager. Generate a highly detailed, professional, and clear BRD."
    )
    
    print("BRD Draft generated successfully.")
    return {"brd_draft": brd_draft}

# 5. QA Agent
def qa_agent(state: BRDState) -> dict:
    print("--- [Agent] Quality Check Agent running ---")
    brd_draft = state.get("brd_draft", "")
    
    prompt_template = load_prompt("qa.txt")
    prompt = prompt_template.format(draft_brd=brd_draft)
    
    final_brd = llm_service.generate(
        prompt=prompt,
        system_instruction="You are a Senior Product Quality Auditor. Polish the BRD and output the complete improved version."
    )
    
    print("Final BRD polished and approved by QA.")
    return {"final_brd": final_brd}

# 6. Localization Agent
def localize_agent(state: BRDState) -> dict:
    print("--- [Agent] Localization Agent running ---")
    final_brd = state.get("final_brd", "")
    language = state.get("language", "English")
    
    if language == "English":
        print("Target language is English. No translation needed.")
        return {"localized_brd": final_brd}
        
    print(f"Translating final BRD to {language}...")
    # Translate the final BRD using translation service
    localized_brd = sarvam_service.translate(
        text=final_brd, 
        source_lang="English", 
        target_lang=language
    )
    
    print(f"BRD localized to {language} successfully.")
    return {"localized_brd": localized_brd}
