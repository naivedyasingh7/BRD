import os
import uuid
import logging
from typing import Dict, Any, List
from crewai import Crew, Process

from backend.graph.state import BRDState
from backend.services.config import is_sarvam_configured, is_groq_configured
from backend.services.audio import transcribe_audio
from backend.services.translation import translate_text
from backend.agents.trace import AgentExecutionTracker
from backend.agents.crews import (
    ClarificationQuestions,
    build_context_task,
    build_requirements_task,
    build_stakeholders_task,
    build_ambiguity_task,
    build_risk_task,
    build_structuring_task,
    build_write_task,
    build_qa_task,
    build_refine_task
)

logger = logging.getLogger(__name__)


def _get_tracker(state: BRDState) -> AgentExecutionTracker:
    request_id = state.get("request_id") or f"req-{uuid.uuid4().hex[:8]}"
    project_name = state.get("project_name") or "Software Project"
    return AgentExecutionTracker(project_name=project_name, request_id=request_id)


def input_agent(state: BRDState) -> dict:
    logger.info("--- [LangGraph Node: Input Processing] ---")
    request_id = state.get("request_id") or f"req-{uuid.uuid4().hex[:8]}"
    
    # Check if input has already been processed
    if state.get("cleaned_input"):
        logger.info("cleaned_input already present - skipping input processing.")
        return {}

    raw_input = state.get("raw_input", "").strip()
    language = state.get("language", "English")
    cleaned_input = ""

    # Differentiate audio vs text file or raw text
    is_audio = raw_input.lower().endswith((".wav", ".mp3", ".m4a", ".ogg", ".webm"))
    
    if is_audio:
        if not is_sarvam_configured():
            raise RuntimeError("SARVAM_API_KEY is not configured. Cannot process audio file.")
        logger.info(f"[{request_id}] Transcribing audio input file: {raw_input}")
        cleaned_input = transcribe_audio(raw_input)
    else:
        # Check translation if non-English text input
        if language.lower() != "english" and raw_input:
            if is_sarvam_configured():
                logger.info(f"[{request_id}] Translating non-English input text from {language} to English.")
                cleaned_input = translate_text(raw_input, source_lang=language, target_lang="English")
            else:
                logger.warning(f"[{request_id}] Sarvam AI not configured. Fallback using raw input text directly.")
                cleaned_input = raw_input
        else:
            cleaned_input = raw_input

    # Parse a project name from the first sentence if not set
    project_name = state.get("project_name")
    if not project_name:
        first_line = cleaned_input.split("\n")[0][:40].strip() if cleaned_input else "Software Project"
        project_name = first_line or "Software Project"

    logger.info(f"[{request_id}] Input processing finished. Project name: {project_name}")
    return {
        "cleaned_input": cleaned_input,
        "project_name": project_name,
        "request_id": request_id
    }


def extract_agent(state: BRDState) -> dict:
    logger.info("--- [LangGraph Node: Discovery Crew (Extract)] ---")
    request_id = state.get("request_id") or f"req-{uuid.uuid4().hex[:8]}"
    
    if state.get("context_analysis") and state.get("extracted_requirements"):
        logger.info("Discovery data already extracted - skipping.")
        return {}

    cleaned_input = state.get("cleaned_input", "")
    if not cleaned_input:
        logger.warning("Empty cleaned input. Skipping discovery.")
        return {}

    if not is_groq_configured():
        raise RuntimeError("GROQ_API_KEY is not configured. Cannot run Discovery Crew.")

    tracker = _get_tracker(state)
    
    # 1. Run Context Task
    tracker.start_trace(step_name="Discovery: Context", agent_role="Context Understanding Analyst")
    task_context = build_context_task(cleaned_input)
    crew_context = Crew(agents=[task_context.agent], tasks=[task_context], process=Process.sequential, verbose=True)
    try:
        res_context = str(crew_context.kickoff())
        tracker.end_trace(output_text=res_context, input_text=cleaned_input, status="Success")
    except Exception as e:
        tracker.end_trace(output_text=str(e), input_text=cleaned_input, status="Failed")
        raise RuntimeError(f"Context analysis failed: {str(e)}")

    # 2. Run Requirements Task
    tracker.start_trace(step_name="Discovery: Requirements", agent_role="Requirement Extraction Specialist")
    task_requirements = build_requirements_task(cleaned_input, res_context)
    crew_requirements = Crew(agents=[task_requirements.agent], tasks=[task_requirements], process=Process.sequential, verbose=True)
    try:
        res_requirements = str(crew_requirements.kickoff())
        tracker.end_trace(output_text=res_requirements, input_text=res_context, status="Success")
    except Exception as e:
        tracker.end_trace(output_text=str(e), input_text=res_context, status="Failed")
        raise RuntimeError(f"Requirement extraction failed: {str(e)}")

    # 3. Run Stakeholder Task
    tracker.start_trace(step_name="Discovery: Stakeholders", agent_role="Stakeholder Analyst")
    task_stakeholders = build_stakeholders_task(cleaned_input, res_context, res_requirements)
    crew_stakeholders = Crew(agents=[task_stakeholders.agent], tasks=[task_stakeholders], process=Process.sequential, verbose=True)
    try:
        res_stakeholders = str(crew_stakeholders.kickoff())
        tracker.end_trace(output_text=res_stakeholders, input_text=res_requirements, status="Success")
    except Exception as e:
        tracker.end_trace(output_text=str(e), input_text=res_requirements, status="Failed")
        raise RuntimeError(f"Stakeholder extraction failed: {str(e)}")

    # Update state
    agent_traces = state.get("agent_traces", []) + tracker.traces
    structured_data = {
        "context": res_context,
        "requirements": res_requirements,
        "stakeholders": res_stakeholders
    }
    
    return {
        "context_analysis": res_context,
        "extracted_requirements": res_requirements,
        "stakeholder_analysis": res_stakeholders,
        "structured_data": structured_data,
        "agent_traces": agent_traces
    }


def clarify_agent(state: BRDState) -> dict:
    logger.info("--- [LangGraph Node: Validation Crew (Clarify)] ---")
    request_id = state.get("request_id") or f"req-{uuid.uuid4().hex[:8]}"

    # Check if questions were already generated and answered
    questions = state.get("questions", [])
    answers = state.get("answers", [])
    if questions and len(answers) >= len(questions):
        logger.info("Questions already answered. Skipping clarification.")
        return {}

    if not is_groq_configured():
        raise RuntimeError("GROQ_API_KEY is not configured. Cannot run Validation Crew.")

    tracker = _get_tracker(state)
    context_data = (
        f"Context: {state.get('context_analysis')}\n"
        f"Requirements: {state.get('extracted_requirements')}\n"
        f"Stakeholders: {state.get('stakeholder_analysis')}"
    )

    # 1. Run Ambiguity Task (Structured Output using Pydantic model)
    tracker.start_trace(step_name="Validation: Ambiguity", agent_role="Ambiguity Detector")
    task_ambiguity = build_ambiguity_task(context_data)
    crew_ambiguity = Crew(agents=[task_ambiguity.agent], tasks=[task_ambiguity], process=Process.sequential, verbose=True)
    
    try:
        res_ambiguity = crew_ambiguity.kickoff()
        output_text = str(res_ambiguity)
        
        # Access structured output directly from output_pydantic validation object
        questions_list: List[str] = []
        if task_ambiguity.output and task_ambiguity.output.pydantic:
            pydantic_output: ClarificationQuestions = task_ambiguity.output.pydantic
            questions_list = pydantic_output.questions
        else:
            # Fallback (never regex, but clean schema parsing safety)
            import json
            raw_output = task_ambiguity.output.raw
            try:
                parsed = json.loads(raw_output)
                if isinstance(parsed, list):
                    questions_list = parsed
                elif isinstance(parsed, dict) and "questions" in parsed:
                    questions_list = parsed["questions"]
            except Exception:
                questions_list = ["Could you provide more specific details about this project's requirements?"]
                
        tracker.end_trace(output_text=output_text, input_text=context_data, status="Success")
    except Exception as e:
        tracker.end_trace(output_text=str(e), input_text=context_data, status="Failed")
        raise RuntimeError(f"Ambiguity detection failed: {str(e)}")

    # 2. Run Risk Task
    tracker.start_trace(step_name="Validation: Risks", agent_role="Risk Analyst")
    task_risk = build_risk_task(context_data, output_text)
    crew_risk = Crew(agents=[task_risk.agent], tasks=[task_risk], process=Process.sequential, verbose=True)
    try:
        res_risk = str(crew_risk.kickoff())
        tracker.end_trace(output_text=res_risk, input_text=output_text, status="Success")
    except Exception as e:
        tracker.end_trace(output_text=str(e), input_text=output_text, status="Failed")
        raise RuntimeError(f"Risk analysis failed: {str(e)}")

    # Update state
    agent_traces = state.get("agent_traces", []) + tracker.traces
    
    # Store intermediate risks inside structured_data for legacy compatibility
    structured_data = dict(state.get("structured_data", {}))
    structured_data["risks"] = res_risk

    return {
        "questions": questions_list,
        "ambiguities_analysis": output_text,
        "risks_analysis": res_risk,
        "structured_data": structured_data,
        "agent_traces": agent_traces
    }


def brd_agent(state: BRDState) -> dict:
    logger.info("--- [LangGraph Node: Documentation/Refinement (Generate)] ---")
    request_id = state.get("request_id") or f"req-{uuid.uuid4().hex[:8]}"
    
    brd_draft = state.get("brd_draft", "")
    questions = state.get("questions", [])
    answers = state.get("answers", [])

    if not is_groq_configured():
        raise RuntimeError("GROQ_API_KEY is not configured. Cannot generate BRD.")

    tracker = _get_tracker(state)
    qa_pairs = [f"Q: {q}\nA: {a}" for q, a in zip(questions, answers)]
    clarification_qa = "\n".join(qa_pairs) if qa_pairs else ""

    # REFINEMENT LOOP TRIGGERED
    if brd_draft and answers:
        logger.info(f"[{request_id}] Refinement loop triggered with feedback.")
        feedback = clarification_qa if clarification_qa else "\n".join(answers)
        
        tracker.start_trace(step_name="Refinement: Update", agent_role="Feedback Refinement Specialist")
        task_refine = build_refine_task(brd_draft, feedback)
        crew_refine = Crew(agents=[task_refine.agent], tasks=[task_refine], process=Process.sequential, verbose=True)
        
        try:
            res_refine = str(crew_refine.kickoff())
            tracker.end_trace(output_text=res_refine, input_text=feedback, status="Success")
            
            # Reset answers to prevent endless refinement loop in next invocation
            return {
                "brd_draft": res_refine,
                "final_brd": res_refine,
                "answers": [],
                "agent_traces": state.get("agent_traces", []) + tracker.traces
            }
        except Exception as e:
            tracker.end_trace(output_text=str(e), input_text=feedback, status="Failed")
            raise RuntimeError(f"BRD Refinement failed: {str(e)}")

    # MAIN DOCUMENTATION WORKFLOW
    context_str = (
        f"Context: {state.get('context_analysis')}\n"
        f"Requirements: {state.get('extracted_requirements')}\n"
        f"Stakeholders: {state.get('stakeholder_analysis')}\n"
        f"Risks: {state.get('risks_analysis')}\n"
    )
    if clarification_qa:
        context_str += f"Clarifications:\n{clarification_qa}"

    # 1. Structure outline task
    tracker.start_trace(step_name="Documentation: Outline", agent_role="Requirement Structuring Expert")
    task_structure = build_structuring_task(context_str)
    crew_structure = Crew(agents=[task_structure.agent], tasks=[task_structure], process=Process.sequential, verbose=True)
    try:
        res_structure = str(crew_structure.kickoff())
        tracker.end_trace(output_text=res_structure, input_text=context_str, status="Success")
    except Exception as e:
        tracker.end_trace(output_text=str(e), input_text=context_str, status="Failed")
        raise RuntimeError(f"Outline generation failed: {str(e)}")

    # 2. Write BRD draft task
    tracker.start_trace(step_name="Documentation: Write", agent_role="BRD Author")
    task_write = build_write_task(res_structure)
    crew_write = Crew(agents=[task_write.agent], tasks=[task_write], process=Process.sequential, verbose=True)
    try:
        res_write = str(crew_write.kickoff())
        tracker.end_trace(output_text=res_write, input_text=res_structure, status="Success")
    except Exception as e:
        tracker.end_trace(output_text=str(e), input_text=res_structure, status="Failed")
        raise RuntimeError(f"BRD drafting failed: {str(e)}")

    # 3. QA BRD task
    tracker.start_trace(step_name="Documentation: QA Review", agent_role="BRD Quality Assurance Reviewer")
    task_qa = build_qa_task(res_write)
    crew_qa = Crew(agents=[task_qa.agent], tasks=[task_qa], process=Process.sequential, verbose=True)
    try:
        res_qa = str(crew_qa.kickoff())
        tracker.end_trace(output_text=res_qa, input_text=res_write, status="Success")
    except Exception as e:
        tracker.end_trace(output_text=str(e), input_text=res_write, status="Failed")
        raise RuntimeError(f"QA review failed: {str(e)}")

    # Update state
    agent_traces = state.get("agent_traces", []) + tracker.traces
    return {
        "structured_outline": res_structure,
        "brd_draft": res_write,
        "qa_review": res_qa,
        "final_brd": res_qa,
        "agent_traces": agent_traces
    }


def localize_agent(state: BRDState) -> dict:
    logger.info("--- [LangGraph Node: Localization] ---")
    request_id = state.get("request_id") or f"req-{uuid.uuid4().hex[:8]}"
    
    final_brd = state.get("final_brd", "")
    language = state.get("language", "English")

    if not final_brd:
        logger.warning("Empty final BRD received for translation.")
        return {}

    if language.lower() == "english":
        logger.info(f"[{request_id}] Language preset is English. Skipping translation.")
        return {"localized_brd": final_brd}

    if not is_sarvam_configured():
        logger.warning(f"[{request_id}] Sarvam AI is not configured. Cannot translate BRD. Fallback using English BRD.")
        return {"localized_brd": final_brd}

    try:
        logger.info(f"[{request_id}] Translating final BRD from English to {language}...")
        localized_brd = translate_text(final_brd, source_lang="English", target_lang=language)
        return {"localized_brd": localized_brd}
    except Exception as e:
        logger.error(f"[{request_id}] BRD translation failed: {type(e).__name__} - {str(e)}")
        # Graceful error recovery: don't crash
        err_msg = f"[Translation failed: {type(e).__name__} - {str(e)}]\n\n{final_brd}"
        return {"localized_brd": err_msg}
