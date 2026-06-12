import logging
from langgraph.graph import StateGraph, END
from backend.graph.state import BRDState
from backend.graph.agents import (
    input_agent,
    extract_agent,
    clarify_agent,
    brd_agent,
    localize_agent
)

logger = logging.getLogger(__name__)


def create_workflow():
    builder = StateGraph(BRDState)

    builder.add_node("input", input_agent)
    builder.add_node("extract", extract_agent)
    builder.add_node("clarify", clarify_agent)
    builder.add_node("generate", brd_agent)
    builder.add_node("localize", localize_agent)

    builder.set_entry_point("input")

    builder.add_edge("input", "extract")
    builder.add_edge("extract", "clarify")

    def clarification_router(state: BRDState):
        questions = state.get("questions", [])
        answers = state.get("answers", [])
        if questions and not answers:
            logger.info("--- [Router] Pausing for clarification questions. ---")
            return "pause_for_questions"
        logger.info("--- [Router] Proceeding to BRD Generation. ---")
        return "generate_brd"

    builder.add_conditional_edges(
        "clarify",
        clarification_router,
        {
            "pause_for_questions": END,
            "generate_brd": "generate"
        }
    )

    builder.add_edge("generate", "localize")
    builder.add_edge("localize", END)

    return builder.compile()


graph = create_workflow()
