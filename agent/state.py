"""
Shared state that flows through the LangGraph graph.

Design note: the graph processes ONE uploaded document per run through
classify -> match -> validate, then a separate graph run (or the same
run with checklist context) produces the follow-up draft once all
documents in a batch have been classified. See graph.py for how these
are composed.
"""
from typing import Optional, TypedDict

from app.schema.models import ChecklistItemDefinition


class AgentState(TypedDict, total=False):
    # --- inputs ---
    session_id: str
    document_id: str
    filename: str
    extracted_text: str                      # raw text pulled from the uploaded file
    checklist_items: list[ChecklistItemDefinition]  # the full checklist for this client's template

    # --- populated by classify_document node ---
    detected_type: Optional[str]
    confidence: float
    summary: str

    # --- populated by match_to_checklist node ---
    matched_key: Optional[str]
    match_reasoning: str

    # --- populated by validate_completeness node ---
    is_valid: bool
    flag_reason: Optional[str]

    # --- populated by draft_followup node (batch-level, optional per-run) ---
    missing_items: list[str]
    flagged_items: list[str]
    followup_message: Optional[str]
