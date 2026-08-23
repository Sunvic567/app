"""
Data access layer.

For the 4-day demo this is an in-memory store so the whole thing runs
with zero external setup — no Supabase project needed to see it work.
The method signatures mirror what the Supabase-backed version will look
like (see schema.sql), so swapping this out later for a real
`supabase-py` client should mean changing this file only, not the
routers or agent code that call it.
"""
import uuid
from datetime import datetime

from helper.checklists import CHECKLISTS
from schema.models import (
    ChecklistItemState,
    ClientSession,
    ChecklistTemplateType,
    DocumentStatus,
    UploadedDocument,
)


class InMemoryStore:
    def __init__(self):
        self._sessions: dict[str, ClientSession] = {}
        self._documents: dict[str, list[UploadedDocument]] = {}  # session_id -> docs

    # --- sessions ---
    def create_session(self, client_name: str, checklist_type: ChecklistTemplateType) -> ClientSession:
        session = ClientSession(
            id=str(uuid.uuid4()),
            client_name=client_name,
            checklist_type=checklist_type,
            created_at=datetime.utcnow(),
        )
        self._sessions[session.id] = session
        self._documents[session.id] = []
        return session

    def get_session(self, session_id: str) -> ClientSession | None:
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[ClientSession]:
        return list(self._sessions.values())

    # --- documents ---
    def add_document(self, doc: UploadedDocument) -> None:
        self._documents.setdefault(doc.session_id, []).append(doc)

    def update_document(self, session_id: str, document_id: str, **updates) -> None:
        docs = self._documents.get(session_id, [])
        for doc in docs:
            if doc.id == document_id:
                for key, value in updates.items():
                    setattr(doc, key, value)
                return

    def get_documents(self, session_id: str) -> list[UploadedDocument]:
        return self._documents.get(session_id, [])

    # --- derived checklist state ---
    def get_checklist_state(self, session_id: str) -> list[ChecklistItemState]:
        session = self.get_session(session_id)
        if session is None:
            return []

        definitions = CHECKLISTS[session.checklist_type]
        docs = self.get_documents(session_id)

        # Map each checklist key to the best matching document, if any.
        matches_by_key: dict[str, UploadedDocument] = {}
        for doc in docs:
            if doc.detected_type:
                matches_by_key[doc.detected_type] = doc

        state: list[ChecklistItemState] = []
        for item in definitions:
            matched_doc = matches_by_key.get(item.key)
            if matched_doc is None:
                status = DocumentStatus.MISSING
                flag_reason = None
            elif matched_doc.flag_reason:
                status = DocumentStatus.FLAGGED
                flag_reason = matched_doc.flag_reason
            else:
                status = DocumentStatus.RECEIVED
                flag_reason = None

            state.append(
                ChecklistItemState(
                    key=item.key,
                    label=item.label,
                    required=item.required,
                    status=status,
                    matched_document_id=matched_doc.id if matched_doc else None,
                    flag_reason=flag_reason,
                )
            )
        return state


# Single shared instance for the demo process.
store = InMemoryStore()
