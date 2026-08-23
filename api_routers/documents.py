import uuid

from fastapi import APIRouter, HTTPException, UploadFile

from app.agent.graph import run_document_classification
from app.helper.checklists import CHECKLISTS
from app.helper.extraction import extract_text
from app.schema.models import UploadedDocument
from app.memory.store  import store

router = APIRouter(prefix="/sessions/{session_id}/documents", tags=["documents"])


@router.post("", response_model=UploadedDocument)
async def upload_document(session_id: str, file: UploadFile):
    session = store.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    file_bytes = await file.read()
    extracted = extract_text(file.filename, file_bytes)

    document = UploadedDocument(
        id=str(uuid.uuid4()),
        session_id=session_id,
        filename=file.filename,
    )
    store.add_document(document)

    checklist_items = CHECKLISTS[session.checklist_type]

    try:
        result = run_document_classification(
            session_id=session_id,
            document_id=document.id,
            filename=file.filename,
            extracted_text=extracted,
            checklist_items=checklist_items,
        )
        store.update_document(
            session_id,
            document.id,
            detected_type=result.get("matched_key"),
            confidence=result.get("confidence"),
            extracted_summary=result.get("summary"),
            flag_reason=result.get("flag_reason") if not result.get("is_valid", True) else None,
        )
    except Exception as exc:  # noqa: BLE001 — never let a live demo 500 on a classification hiccup
        store.update_document(
            session_id,
            document.id,
            detected_type=None,
            extracted_summary="Classification failed.",
            flag_reason=f"Could not classify automatically ({type(exc).__name__}) — needs manual review.",
        )

    # Return the updated document
    updated = next(d for d in store.get_documents(session_id) if d.id == document.id)
    return updated
