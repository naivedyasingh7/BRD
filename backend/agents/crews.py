import os
import logging
from typing import List
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, Process

from backend.services.llm import shared_groq_llm



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


# Load system instructions/prompts
PROMPT_EXTRACTION = _load_prompt("extraction.txt")
PROMPT_BRD = _load_prompt("brd.txt")
PROMPT_QA = _load_prompt("qa.txt")

# Pydantic models for structured outputs
class ClarificationQuestions(BaseModel):
    questions: List[str] = Field(
        ..., 
        description="A list of 2 to 4 crucial clarification questions to ask the user. Must be specific and highly relevant."
    )


# ----------------------------------------------------
# 1. Discovery Crew Agents
# ----------------------------------------------------
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

# ----------------------------------------------------
# 2. Validation Crew Agents
# ----------------------------------------------------
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

# ----------------------------------------------------
# 3. Documentation Crew Agents
# ----------------------------------------------------
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

# ----------------------------------------------------
# 4. Refinement Crew Agents
# ----------------------------------------------------
refinement_agent = Agent(
    role="Feedback Refinement Specialist",
    goal="Analyze user feedback and update the specific sections of the BRD affected by the feedback.",
    backstory="You are a patient and precise editor who seamlessly integrates client feedback into existing technical documents.",
    llm=shared_groq_llm,
    verbose=True
)


# ----------------------------------------------------
# Discovery Task Builders
# ----------------------------------------------------
def build_context_task(cleaned_input: str) -> Task:
    extraction_instructions = PROMPT_EXTRACTION + "\n\n" if PROMPT_EXTRACTION else ""
    return Task(
        description=f"{extraction_instructions}Analyze the following transcript and determine the project domain, core problem, and objectives.\nTranscript:\n{cleaned_input}",
        expected_output="A structured summary with: Domain, Problem Statement, Primary Objectives (bullet list), and Key Constraints.",
        agent=context_agent
    )


def build_requirements_task(cleaned_input: str, context_text: str) -> Task:
    extraction_instructions = PROMPT_EXTRACTION + "\n\n" if PROMPT_EXTRACTION else ""
    return Task(
        description=f"{extraction_instructions}Using the context analysis below, extract ALL functional and non-functional requirements from the transcript. Label each as FUNCTIONAL or NON-FUNCTIONAL. Be exhaustive.\n\nContext Analysis:\n{context_text}\n\nTranscript:\n{cleaned_input}",
        expected_output="Two clearly labelled lists: Functional Requirements and Non-Functional Requirements, each as bullet points.",
        agent=requirement_agent
    )


def build_stakeholders_task(cleaned_input: str, context_text: str, requirements_text: str) -> Task:
    extraction_instructions = PROMPT_EXTRACTION + "\n\n" if PROMPT_EXTRACTION else ""
    return Task(
        description=f"{extraction_instructions}Using the context and requirements below, identify all stakeholders, user personas, and external systems.\n\nContext Analysis:\n{context_text}\n\nRequirements:\n{requirements_text}\n\nTranscript:\n{cleaned_input}",
        expected_output="A list of stakeholders with Name, Role, and Key Interests for each.",
        agent=stakeholder_agent
    )


# ----------------------------------------------------
# Validation Task Builders
# ----------------------------------------------------
def build_ambiguity_task(context_data: str) -> Task:
    return Task(
        description=f"Review the extracted project details and identify ambiguities. Generate 2 to 4 crucial clarification questions to ask the user.\n\nProject Details: {context_data}",
        expected_output="A structured list of clarification questions.",
        agent=ambiguity_agent,
        output_pydantic=ClarificationQuestions
    )


def build_risk_task(context_data: str, ambiguities_text: str) -> Task:
    return Task(
        description=f"Analyze the project details and identified ambiguities for assumptions, dependencies, and potential risks.\n\nProject Details: {context_data}\n\nIdentified Ambiguities: {ambiguities_text}",
        expected_output="A list of risks, assumptions, and dependencies.",
        agent=risk_agent
    )


# ----------------------------------------------------
# Documentation Task Builders
# ----------------------------------------------------
def build_structuring_task(context_str: str) -> Task:
    return Task(
        description=(
            f"Organize the following extracted project data into a complete BRD outline with these sections: "
            f"Executive Summary, Project Objectives, Scope (In/Out), Stakeholders, Functional Requirements (with IDs REQ-1.0 etc), "
            f"Non-Functional Requirements, Assumptions & Dependencies, Risks & Mitigations, User Stories, Acceptance Criteria.\n"
            f"Data:\n{context_str}"
        ),
        expected_output="A detailed BRD outline with all 10 sections populated. Every functional requirement must have an ID, title, description, and status.",
        agent=structuring_agent
    )


def build_write_task(structured_outline: str) -> Task:
    brd_instructions = PROMPT_BRD + "\n\n" if PROMPT_BRD else ""
    return Task(
        description=f"{brd_instructions}Using the structured outline below, write the COMPLETE Business Requirements Document in Markdown. Do not skip or abbreviate any section. Every requirement must have a unique ID.\n\nOutline:\n{structured_outline}",
        expected_output="A complete, professional BRD in Markdown with all 10 sections fully written. No placeholders, no TODOs.",
        agent=brd_gen_agent
    )


def build_qa_task(brd_draft: str) -> Task:
    qa_instructions = PROMPT_QA + "\n\n" if PROMPT_QA else ""
    return Task(
        description=f"{qa_instructions}Review the BRD draft below. Fix inconsistencies, ensure every risk has a mitigation, every acceptance criterion is testable, and all stakeholders in requirements appear in the Stakeholders section. Return the FULL corrected document.\n\nDraft BRD:\n{brd_draft}",
        expected_output="The final, audit-ready BRD in Markdown. Complete document — do not summarize.",
        agent=qa_doc_agent
    )


# ----------------------------------------------------
# Refinement Task Builders
# ----------------------------------------------------
def build_refine_task(brd_draft: str, feedback: str) -> Task:
    return Task(
        description=f"Update the existing BRD draft incorporating the following user feedback. Preserve all sections not affected by the feedback.\n\nFeedback:\n{feedback}\n\nExisting BRD:\n{brd_draft}",
        expected_output="The fully updated, complete Business Requirements Document in Markdown format.",
        agent=refinement_agent
    )
