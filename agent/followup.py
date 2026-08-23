"""
Session-level follow-up drafting. Looks at the full checklist state for
a client (not just one document) and drafts one consolidated message
listing everything still missing or flagged.
"""
from app.agent.llm import draft_followup as llm_draft_followup
from app.schema.models import ChecklistItemState, DocumentStatus


def build_followup_message(client_name: str, checklist_state: list[ChecklistItemState]) -> str | None:
    missing = [
        item.label
        for item in checklist_state
        if item.status == DocumentStatus.MISSING and item.required
    ]
    flagged = [
        {"label": item.label, "reason": item.flag_reason or "needs review"}
        for item in checklist_state
        if item.status == DocumentStatus.FLAGGED
    ]

    if not missing and not flagged:
        return None  # nothing to chase — checklist is complete

    return llm_draft_followup(client_name, missing, flagged)
