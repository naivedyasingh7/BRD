from langgraph.graph import StateGraph, END
from backend.graph.state import BRDState
from backend.graph.agents import (
    input_agent,
    extract_agent,
    clarify_agent,
    brd_agent,
    qa_agent,
    localize_agent
)

def create_workflow():
    builder = StateGraph(BRDState)

    # Register nodes
    builder.add_node("input", input_agent)
    builder.add_node("extract", extract_agent)
    builder.add_node("clarify", clarify_agent)
    builder.add_node("generate", brd_agent)
    builder.add_node("qa", qa_agent)
    builder.add_node("localize", localize_agent)

    # Set entry point
    builder.set_entry_point("input")

    # Static transitions
    builder.add_edge("input", "extract")
    builder.add_edge("extract", "clarify")

    # Conditional routing after clarification
    def clarification_router(state: BRDState):
        questions = state.get("questions", [])
        answers = state.get("answers", [])
        
        # If questions were generated but we don't have answers yet,
        # we finish execution to return the questions to the client.
        if questions and not answers:
            print("--- [Router] Clarification questions generated. Pausing for user feedback. ---")
            return "pause_for_questions"
        
        print("--- [Router] Proceeding directly to BRD Generation. ---")
        return "generate_brd"

    builder.add_conditional_edges(
        "clarify",
        clarification_router,
        {
            "pause_for_questions": END,
            "generate_brd": "generate"
        }
    )

    # Final static path
    builder.add_edge("generate", "qa")
    builder.add_edge("qa", "localize")
    builder.add_edge("localize", END)

    return builder.compile()

# Compile graph
graph = create_workflow()
