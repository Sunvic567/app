"""
Node functions for the onboarding graph. Each node takes the AgentState
and returns a dict of the fields it updates — standard LangGraph pattern.
"""
from agent.llm import classify_document as llm_classify

from agent.state import AgentState


def classify_document_node(state: AgentState) -> dict:
    """Classify the uploaded document's extracted text against the checklist."""
    checklist_dicts = [
        {"key": item.key, "label": item.label, "description": item.description}
        for item in state["checklist_items"]
    ]
    result = llm_classify(state["extracted_text"], checklist_dicts)

    return {
        "detected_type": result.get("detected_type"),
        "confidence": result.get("confidence", 0.0),
        "summary": result.get("summary", ""),
        "is_valid": result.get("is_valid", True),
        "flag_reason": result.get("flag_reason"),
    }


def match_to_checklist_node(state: AgentState) -> dict:
    """
    Confirm the classifier's detected_type actually exists in this client's
    checklist (the classifier only sees the checklist it was given, so this
    is mostly a safety net for confidence thresholds and typos).
    """
    valid_keys = {item.key for item in state["checklist_items"]}
    detected = state.get("detected_type")
    confidence = state.get("confidence", 0.0)

    LOW_CONFIDENCE_THRESHOLD = 0.55

    if detected in valid_keys and confidence >= LOW_CONFIDENCE_THRESHOLD:
        return {
            "matched_key": detected,
            "match_reasoning": f"Matched to '{detected}' at confidence {confidence:.2f}",
        }

    return {
        "matched_key": None,
        "match_reasoning": (
            f"No confident match (detected='{detected}', confidence={confidence:.2f})"
        ),
    }


def validate_completeness_node(state: AgentState) -> dict:
    """
    Final validity check combining the classifier's own is_valid flag with
    whether we actually got a checklist match at all.
    """
    if state.get("matched_key") is None:
        return {
            "is_valid": False,
            "flag_reason": state.get("flag_reason")
            or "Could not confidently match this document to an expected type.",
        }

    # Trust the classifier's is_valid/flag_reason if we did get a match.
    return {
        "is_valid": state.get("is_valid", True),
        "flag_reason": state.get("flag_reason"),
    }
