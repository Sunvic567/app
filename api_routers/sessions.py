from fastapi import APIRouter, HTTPException

from schema.models import ChecklistTemplateType, ClientSession, SessionStateResponse
from memory.store import store

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=ClientSession)
def create_session(client_name: str, checklist_type: ChecklistTemplateType):
    """Start a new simulated client onboarding session."""
    return store.create_session(client_name=client_name, checklist_type=checklist_type)


@router.get("", response_model=list[ClientSession])
def list_sessions():
    return store.list_sessions()


@router.get("/{session_id}", response_model=SessionStateResponse)
def get_session_state(session_id: str):
    session = store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    checklist = store.get_checklist_state(session_id)
    total = len(checklist)
    done = sum(1 for item in checklist if item.status.value == "received")
    completion_pct = round((done / total) * 100, 1) if total else 0.0

    return SessionStateResponse(
        session=session,
        checklist=checklist,
        completion_pct=completion_pct,
        followup_message=None,
    )
