import json
import logging
from crewai import Agent, Task, Crew, Process
from pydantic import BaseModel, Field
from typing import List

from backend.graph.state import BRDState
from backend.services.sarvam import sarvam_service
from backend.services.llm import shared_groq_llm

if shared_groq_llm is None:
    raise ImportError("GROQ_API_KEY is not configured. Set it in your .env file to use the AI agents.")

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# CrewAI Agents Definition
# ---------------------------------------------------------

context_agent = Agent(
    role="Context Understanding Analyst",
    goal="Analyze transcripts to identify the project domain, primary objectives, and core business problem.",
    backstory="You are an expert business analyst who specializes in understanding the root cause of business problems from unstructured conversations.",
    llm=shared_groq_llm,
    verbose=True
)

requirement_agent = Agent(
    role="Requirement Extraction Specialist",
    goal="Extract distinct functional and non-functional requirements from raw transcripts.",
    backstory="You have a keen eye for technical details and can distill complex conversations into actionable software requirements.",
    llm=shared_groq_llm,
    verbose=True
)

stakeholder_agent = Agent(
    role="Stakeholder Analyst",
    goal="Identify all user personas, actors, and stakeholders mentioned or implied in the context.",
    backstory="You are an expert in user experience and systems architecture, mapping out who uses the system and how they interact with it.",
    llm=shared_groq_llm,
    verbose=True
)

ambiguity_agent = Agent(
    role="Ambiguity Detector",
    goal="Detect vague requirements, missing information, and generate clarification questions for the user.",
    backstory="You are a meticulous QA engineer and Business Analyst. You never assume; you always ask when details are fuzzy.",
    llm=shared_groq_llm,
    verbose=True
)

risk_agent = Agent(
    role="Risk Analyst",
    goal="Identify assumptions, dependencies, potential blockers, and project risks.",
    backstory="You are a seasoned Project Manager who foresees technical and business risks before they happen.",
    llm=shared_groq_llm,
    verbose=True
)

structuring_agent = Agent(
    role="Requirement Structuring Expert",
    goal="Organize requirements into logical categories, hierarchies, and sections.",
    backstory="You are a technical writer who turns chaotic lists of requirements into beautifully structured architectures.",
    llm=shared_groq_llm,
    verbose=True
)

brd_gen_agent = Agent(
    role="BRD Author",
    goal="Write the complete, professional Business Requirement Document using the structured requirements, context, and clarification answers.",
    backstory="You are an elite enterprise software architect who writes comprehensive, industry-standard BRDs.",
    llm=shared_groq_llm,
    verbose=True
)

qa_doc_agent = Agent(
    role="BRD Quality Assurance Reviewer",
    goal="Review the generated BRD for completeness, consistency, formatting standards, and ensure no placeholders remain.",
    backstory="You are a strict technical auditor. You ensure every BRD meets the highest enterprise standards before delivery.",
    llm=shared_groq_llm,
    verbose=True
)

refinement_agent = Agent(
    role="Feedback Refinement Specialist",
    goal="Analyze user feedback and update the specific sections of the BRD affected by the feedback.",
    backstory="You are a patient and precise editor who seamlessly integrates client feedback into existing technical documents.",
    llm=shared_groq_llm,
    verbose=True
)

# ---------------------------------------------------------
# LangGraph Node Implementations
# ---------------------------------------------------------

def input_agent(state: BRDState) -> dict:
    """1. Input Agent: Handles Sarvam STT and initial translation/cleaning."""
    logger.info("--- [LangGraph] Input Node running ---")
    raw_input = state.get("raw_input", "").strip()
    language = state.get("language", "English")

    if raw_input.lower().endswith((".wav", ".mp3", ".m4a", ".ogg", ".webm")):
        logger.info(f"Processing audio input: {raw_input}")
        if sarvam_service is None:
            raise RuntimeError("SARVAM_API_KEY is not configured. Cannot process audio files.")
        cleaned_input = sarvam_service.speech_to_text_translate(raw_input)
    else:
        logger.info(f"Processing text input. Language: {language}")
        if language != "English" and raw_input:
            if sarvam_service is not None:
                cleaned_input = sarvam_service.translate(raw_input, source_lang=language, target_lang="English")
            else:
                logger.warning("SARVAM_API_KEY not set — skipping translation, using raw input as-is.")
                cleaned_input = raw_input
        else:
            cleaned_input = raw_input

    logger.info("Input cleaned successfully.")
    return {"cleaned_input": cleaned_input}


def extract_agent(state: BRDState) -> dict:
    """2. Extract Agent: Runs the Discovery Crew."""
    logger.info("--- [LangGraph] Extract Node (Discovery Crew) running ---")
    cleaned_input = state.get("cleaned_input", "")

    if not cleaned_input:
        logger.warning("Empty cleaned input received. Skipping extraction.")
        return {"structured_data": {}}

    task_context = Task(
        description=f"Analyze the following transcript and determine the project domain, core problem, and objectives.\nTranscript: {cleaned_input}",
        expected_output="A summary of the business context, domain, problem statement, and objectives.",
        agent=context_agent
    )

    task_requirements = Task(
        description=f"Extract functional and non-functional requirements from the transcript.\nTranscript: {cleaned_input}",
        expected_output="A list of functional and non-functional requirements.",
        agent=requirement_agent
    )

    task_stakeholders = Task(
        description=f"Identify all user personas and stakeholders from the transcript.\nTranscript: {cleaned_input}",
        expected_output="A list of stakeholders and their roles.",
        agent=stakeholder_agent
    )

    discovery_crew = Crew(
        agents=[context_agent, requirement_agent, stakeholder_agent],
        tasks=[task_context, task_requirements, task_stakeholders],
        process=Process.sequential,
        verbose=True
    )

    try:
        discovery_output = discovery_crew.kickoff()
        structured_data = {
            "context": task_context.output.raw if task_context.output else "",
            "requirements": task_requirements.output.raw if task_requirements.output else "",
            "stakeholders": task_stakeholders.output.raw if task_stakeholders.output else "",
            "raw_crew_output": str(discovery_output)
        }
        logger.info("Discovery Crew execution completed successfully.")
        return {"structured_data": structured_data}
    except Exception as e:
        logger.error(f"Discovery Crew failed: {e}")
        raise RuntimeError(f"Requirement extraction failed: {str(e)}")


def clarify_agent(state: BRDState) -> dict:
    """3. Clarify Agent: Runs the Validation Crew."""
    logger.info("--- [LangGraph] Clarify Node (Validation Crew) running ---")
    questions = state.get("questions", [])
    answers = state.get("answers", [])

    if questions and len(answers) >= len(questions):
        logger.info("Questions already answered or feedback provided. Skipping clarification generation.")
        return {}

    structured_data = state.get("structured_data", {})
    context_data = str(structured_data)

    task_ambiguity = Task(
        description=f"Review the extracted project details and identify ambiguities. Generate a JSON list of 2 to 4 crucial clarification questions to ask the user. Return ONLY valid JSON array.\nProject Details: {context_data}",
        expected_output="A valid JSON array of strings containing the questions. Example: [\"Question 1?\", \"Question 2?\"]",
        agent=ambiguity_agent
    )

    task_risk = Task(
        description=f"Analyze the project details for assumptions, dependencies, and potential risks.\nProject Details: {context_data}",
        expected_output="A list of risks, assumptions, and dependencies.",
        agent=risk_agent
    )

    validation_crew = Crew(
        agents=[ambiguity_agent, risk_agent],
        tasks=[task_ambiguity, task_risk],
        process=Process.sequential,
        verbose=True
    )

    try:
        validation_crew.kickoff()
    except Exception as e:
        logger.error(f"Validation Crew failed: {e}")
        raise RuntimeError(f"Validation analysis failed: {str(e)}")

    generated_questions = []
    try:
        if task_ambiguity.output:
            raw_q = task_ambiguity.output.raw
            if "```json" in raw_q:
                raw_q = raw_q.split("```json")[1].split("```")[0]
            elif "```" in raw_q:
                raw_q = raw_q.split("```")[1].split("```")[0]
            
            parsed_questions = json.loads(raw_q.strip())
            if isinstance(parsed_questions, list):
                generated_questions = parsed_questions
            else:
                generated_questions = [str(parsed_questions)]
    except Exception as e:
        logger.error(f"Could not parse questions JSON: {e}")
        generated_questions = ["Could you provide more specific technical requirements for this project?"]

    state["structured_data"]["risks"] = task_risk.output.raw if task_risk.output else ""
    logger.info(f"Validation completed. {len(generated_questions)} questions generated.")
    
    return {"questions": generated_questions, "structured_data": state["structured_data"]}


def brd_agent(state: BRDState) -> dict:
    """4. BRD Generator Agent: Runs Documentation Crew & Refinement Crew."""
    logger.info("--- [LangGraph] BRD Generator Node running ---")
    structured_data = state.get("structured_data", {})
    questions = state.get("questions", [])
    answers = state.get("answers", [])
    brd_draft = state.get("brd_draft", "")

    qa_pairs = []
    for q, a in zip(questions, answers):
        qa_pairs.append(f"Q: {q}\nA: {a}")
    clarification_qa = "\n".join(qa_pairs) if qa_pairs else "No clarification questions were answered."

    if brd_draft and answers:
        logger.info("--- [Refinement Flow Triggered] ---")
        task_refine = Task(
            description=f"Update the existing BRD draft incorporating the user's feedback/answers.\nFeedback: {clarification_qa}\nExisting BRD:\n{brd_draft}",
            expected_output="The fully updated, complete Business Requirements Document in Markdown format.",
            agent=refinement_agent
        )
        refine_crew = Crew(agents=[refinement_agent], tasks=[task_refine], process=Process.sequential, verbose=True)
        try:
            result = refine_crew.kickoff()
            logger.info("Refinement completed successfully.")
            return {"brd_draft": str(result)}
        except Exception as e:
            logger.error(f"Refinement Crew failed: {e}")
            raise RuntimeError(f"BRD Refinement failed: {str(e)}")

    logger.info("--- [Documentation Generation Flow Triggered] ---")
    context_str = f"Context: {structured_data.get('context')}\nRequirements: {structured_data.get('requirements')}\nStakeholders: {structured_data.get('stakeholders')}\nRisks: {structured_data.get('risks')}\nClarifications:\n{clarification_qa}"

    task_structure = Task(
        description=f"Organize the following project data into logical BRD sections (Exec Summary, Scope, Requirements, Risks, etc.).\nData: {context_str}",
        expected_output="A detailed outline and structured hierarchy of requirements.",
        agent=structuring_agent
    )

    task_write = Task(
        description="Write the complete Business Requirements Document (BRD) in Markdown format based on the structured hierarchy.",
        expected_output="A professional, comprehensive BRD in Markdown.",
        agent=brd_gen_agent
    )

    task_qa = Task(
        description="Review the drafted BRD. Fix any formatting issues, ensure completeness, and remove any filler text. Provide the final approved Markdown document.",
        expected_output="The final, polished BRD in Markdown.",
        agent=qa_doc_agent
    )

    doc_crew = Crew(
        agents=[structuring_agent, brd_gen_agent, qa_doc_agent],
        tasks=[task_structure, task_write, task_qa],
        process=Process.sequential,
        verbose=True
    )

    try:
        final_result = doc_crew.kickoff()
        logger.info("Documentation Crew completed successfully.")
        return {"brd_draft": str(final_result)}
    except Exception as e:
        logger.error(f"Documentation Crew failed: {e}")
        raise RuntimeError(f"BRD Generation failed: {str(e)}")


def qa_agent(state: BRDState) -> dict:
    """5. QA Agent: Pass-through node."""
    logger.info("--- [LangGraph] QA Node (Pass-through) running ---")
    brd_draft = state.get("brd_draft", "")
    return {"final_brd": brd_draft}


def localize_agent(state: BRDState) -> dict:
    """6. Localization Agent: Runs Sarvam AI for translation."""
    logger.info("--- [LangGraph] Localization Node running ---")
    final_brd = state.get("final_brd", "")
    language = state.get("language", "English")
    
    if language == "English":
        logger.info("Target language is English. No translation needed.")
        return {"localized_brd": final_brd}
        
    logger.info(f"Translating final BRD to {language} via Sarvam AI...")
    try:
        if sarvam_service is None:
            logger.warning("SARVAM_API_KEY not set — returning English BRD as localized output.")
            return {"localized_brd": final_brd}
        localized_brd = sarvam_service.translate(
            text=final_brd, 
            source_lang="English", 
            target_lang=language
        )
        logger.info(f"BRD localized to {language} successfully.")
        return {"localized_brd": localized_brd}
    except Exception as e:
        logger.error(f"Localization failed: {e}")
        # If translation fails at the very end, we still have the English BRD.
        # We can return an error string in the localization output to avoid losing the whole run.
        return {"localized_brd": f"[Translation failed due to API error: {e}]\n\nPlease refer to the English BRD."}
