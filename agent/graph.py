"""
Builds and compiles the per-document classification graph.

Flow: classify_document -> match_to_checklist -> validate_completeness

This graph runs once per uploaded document. The separate, session-level
follow-up drafting step (which needs the state of ALL documents in a
session, not just one) lives in followup.py and is called directly from
the API layer rather than embedded in this graph — keeps the per-document
graph simple and independently testable.
"""
from langgraph.graph import StateGraph, END

from agent.nodes import (
    classify_document_node,
    match_to_checklist_node,
    validate_completeness_node,
)
from agent.state import AgentState


def build_document_graph():
    graph = StateGraph(AgentState)

    graph.add_node("classify_document", classify_document_node)
    graph.add_node("match_to_checklist", match_to_checklist_node)
    graph.add_node("validate_completeness", validate_completeness_node)

    graph.set_entry_point("classify_document")
    graph.add_edge("classify_document", "match_to_checklist")
    graph.add_edge("match_to_checklist", "validate_completeness")
    graph.add_edge("validate_completeness", END)

    return graph.compile()


# Compiled once at import time; reused across requests.
document_graph = build_document_graph()


def run_document_classification(
    session_id: str,
    document_id: str,
    filename: str,
    extracted_text: str,
    checklist_items,
) -> AgentState:
    """Convenience wrapper the API layer calls for one uploaded document."""
    initial_state: AgentState = {
        "session_id": session_id,
        "document_id": document_id,
        "filename": filename,
        "extracted_text": extracted_text,
        "checklist_items": checklist_items,
    }
    return document_graph.invoke(initial_state)
