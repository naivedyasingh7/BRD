import json
import logging
import os
from crewai import Agent, Task, Crew, Process

from backend.graph.state import BRDState
from backend.services.sarvam import sarvam_service
from backend.services.llm import shared_groq_llm

if shared_groq_llm is None:
    raise ImportError("GROQ_API_KEY is not configured. Set it in your .env file to use the AI agents.")

logger = logging.getLogger(__name__)

PROMPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "prompts")

def _load_prompt(filename: str) -> str:
    path = os.path.join(PROMPTS_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        logger.warning(f"Prompt file not found: {path}")
        return ""

PROMPT_EXTRACTION = _load_prompt("extraction.txt")
PROMPT_BRD = _load_prompt("brd.txt")
PROMPT_QA = _load_prompt("qa.txt")

context_agent = Agent(
    role="Context Understanding Analyst",
    goal="Analyze transcripts to identify the project domain, primary objectives, and core business problem.",
    backstory=PROMPT_EXTRACTION or "You are an expert business analyst who specializes in understanding the root cause of business problems from unstructured conversations.",
    llm=shared_groq_llm,
    verbose=True
)

requirement_agent = Agent(
    role="Requirement Extraction Specialist",
    goal="Extract distinct functional and non-functional requirements from raw transcripts.",
    backstory=PROMPT_EXTRACTION or "You have a keen eye for technical details and can distill complex conversations into actionable software requirements.",
    llm=shared_groq_llm,
    verbose=True
)

stakeholder_agent = Agent(
    role="Stakeholder Analyst",
    goal="Identify all user personas, actors, and stakeholders mentioned or implied in the context.",
    backstory=PROMPT_EXTRACTION or "You are an expert in user experience and systems architecture, mapping out who uses the system and how they interact with it.",
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
    backstory=PROMPT_BRD or "You are an elite enterprise software architect who writes comprehensive, industry-standard BRDs.",
    llm=shared_groq_llm,
    verbose=True
)

qa_doc_agent = Agent(
    role="BRD Quality Assurance Reviewer",
    goal="Review the generated BRD for completeness, consistency, formatting standards, and ensure no placeholders remain.",
    backstory=PROMPT_QA or "You are a strict technical auditor. You ensure every BRD meets the highest enterprise standards before delivery.",
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


def input_agent(state: BRDState) -> dict:
    logger.info("--- [LangGraph] Input Node running ---")

    if state.get("cleaned_input"):
        logger.info("cleaned_input already present — skipping input processing.")
        return {}

    raw_input = state.get("raw_input", "").strip()
    language = state.get("language", "English")

    if raw_input.lower().endswith((".wav", ".mp3", ".m4a", ".ogg", ".webm")):
        if sarvam_service is None:
            raise RuntimeError("SARVAM_API_KEY is not configured. Cannot process audio files.")
        cleaned_input = sarvam_service.speech_to_text_translate(raw_input)
    else:
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
    logger.info("--- [LangGraph] Extract Node (Discovery Crew) running ---")

    if state.get("structured_data"):
        logger.info("structured_data already present — skipping extraction.")
        return {}

    cleaned_input = state.get("cleaned_input", "")
    if not cleaned_input:
        logger.warning("Empty cleaned input received. Skipping extraction.")
        return {"structured_data": {}}

    extraction_instructions = PROMPT_EXTRACTION + "\n\n" if PROMPT_EXTRACTION else ""

    task_context = Task(
        description=f"{extraction_instructions}Analyze the following transcript and determine the project domain, core problem, and objectives.\nTranscript: {cleaned_input}",
        expected_output="A summary of the business context, domain, problem statement, and objectives.",
        agent=context_agent
    )
    task_requirements = Task(
        description=f"{extraction_instructions}Extract functional and non-functional requirements from the transcript.\nTranscript: {cleaned_input}",
        expected_output="A list of functional and non-functional requirements.",
        agent=requirement_agent
    )
    task_stakeholders = Task(
        description=f"{extraction_instructions}Identify all user personas and stakeholders from the transcript.\nTranscript: {cleaned_input}",
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
        logger.error(f"Discovery Crew failed: {type(e).__name__}")
        raise RuntimeError(f"Requirement extraction failed: {str(e)}")


def clarify_agent(state: BRDState) -> dict:
    logger.info("--- [LangGraph] Clarify Node (Validation Crew) running ---")
    questions = state.get("questions", [])
    answers = state.get("answers", [])

    if questions and len(answers) >= len(questions):
        logger.info("Questions already answered. Skipping clarification generation.")
        return {}

    structured_data = state.get("structured_data", {})
    context_data = str(structured_data)

    task_ambiguity = Task(
        description=f"Review the extracted project details and identify ambiguities. Generate a JSON list of 2 to 4 crucial clarification questions to ask the user. Return ONLY valid JSON array.\nProject Details: {context_data}",
        expected_output='A valid JSON array of strings. Example: ["Question 1?", "Question 2?"]',
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
        logger.error(f"Validation Crew failed: {type(e).__name__}")
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
            generated_questions = parsed_questions if isinstance(parsed_questions, list) else [str(parsed_questions)]
    except Exception as e:
        logger.error(f"Could not parse questions JSON: {type(e).__name__}")
        generated_questions = ["Could you provide more specific technical requirements for this project?"]

    risks_text = task_risk.output.raw if task_risk.output else ""
    updated_structured_data = {**structured_data, "risks": risks_text}

    logger.info(f"Validation completed. {len(generated_questions)} questions generated.")
    return {"questions": generated_questions, "structured_data": updated_structured_data}


def brd_agent(state: BRDState) -> dict:
    logger.info("--- [LangGraph] BRD Generator Node running ---")
    structured_data = state.get("structured_data", {})
    questions = state.get("questions", [])
    answers = state.get("answers", [])
    brd_draft = state.get("brd_draft", "")

    qa_pairs = [f"Q: {q}\nA: {a}" for q, a in zip(questions, answers)]
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
            final = str(result)
            return {"brd_draft": final, "final_brd": final}
        except Exception as e:
            logger.error(f"Refinement Crew failed: {type(e).__name__}")
            raise RuntimeError(f"BRD Refinement failed: {str(e)}")

    logger.info("--- [Documentation Generation Flow Triggered] ---")
    context_str = (
        f"Context: {structured_data.get('context')}\n"
        f"Requirements: {structured_data.get('requirements')}\n"
        f"Stakeholders: {structured_data.get('stakeholders')}\n"
        f"Risks: {structured_data.get('risks')}\n"
        f"Clarifications:\n{clarification_qa}"
    )

    task_structure = Task(
        description=f"Organize the following project data into logical BRD sections (Exec Summary, Scope, Requirements, Risks, etc.).\nData: {context_str}",
        expected_output="A detailed outline and structured hierarchy of requirements.",
        agent=structuring_agent
    )
    brd_instructions = PROMPT_BRD + "\n\n" if PROMPT_BRD else ""
    qa_instructions = PROMPT_QA + "\n\n" if PROMPT_QA else ""

    task_write = Task(
        description=f"{brd_instructions}Write the complete Business Requirements Document (BRD) in Markdown format based on the structured hierarchy.",
        expected_output="A professional, comprehensive BRD in Markdown.",
        agent=brd_gen_agent
    )
    task_qa = Task(
        description=f"{qa_instructions}Review the drafted BRD. Fix any formatting issues, ensure completeness, and remove any filler text. Provide the final approved Markdown document.",
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
        final = str(final_result)
        return {"brd_draft": final, "final_brd": final}
    except Exception as e:
        logger.error(f"Documentation Crew failed: {type(e).__name__}")
        raise RuntimeError(f"BRD Generation failed: {str(e)}")


def localize_agent(state: BRDState) -> dict:
    logger.info("--- [LangGraph] Localization Node running ---")
    final_brd = state.get("final_brd", "")
    language = state.get("language", "English")

    if language == "English":
        return {"localized_brd": final_brd}

    try:
        if sarvam_service is None:
            logger.warning("SARVAM_API_KEY not set — returning English BRD as localized output.")
            return {"localized_brd": final_brd}
        localized_brd = sarvam_service.translate(text=final_brd, source_lang="English", target_lang=language)
        logger.info(f"BRD localized to {language} successfully.")
        return {"localized_brd": localized_brd}
    except Exception as e:
        logger.error(f"Localization failed: {type(e).__name__}")
        return {"localized_brd": f"[Translation failed: {type(e).__name__}]\n\nPlease refer to the English BRD above."}
