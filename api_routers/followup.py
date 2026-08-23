from fastapi import APIRouter, HTTPException

from app.agent.followup import build_followup_message
from app.memory.store import store

router = APIRouter(prefix="/sessions/{session_id}/followup", tags=["followup"])


@router.post("")
def generate_followup(session_id: str):
    session = store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    checklist_state = store.get_checklist_state(session_id)
    message = build_followup_message(session.client_name, checklist_state)

    if message is None:
        return {"followup_message": None, "note": "Checklist is complete — nothing to chase."}

    return {"followup_message": message}
