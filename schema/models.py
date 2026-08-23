"""
Pydantic models shared across the API and the LangGraph agent.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class DocumentStatus(str, Enum):
    RECEIVED = "received"           # matched a checklist item cleanly
    FLAGGED = "flagged"             # received but wrong type / illegible / expired
    MISSING = "missing"             # checklist item with nothing uploaded yet


class ChecklistTemplateType(str, Enum):
    NEW_BUSINESS_BOOKKEEPING = "new_business_bookkeeping"
    INDIVIDUAL_TAX = "individual_tax"
    CROSS_BORDER = "cross_border"


class ChecklistItemDefinition(BaseModel):
    """One required document type within a checklist template."""
    key: str                      # stable identifier, e.g. "ein_letter"
    label: str                    # human label, e.g. "EIN Confirmation Letter (CP 575)"
    description: str              # what the agent should look for
    required: bool = True


class ClientSession(BaseModel):
    """One simulated client going through onboarding."""
    id: str
    client_name: str
    checklist_type: ChecklistTemplateType
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UploadedDocument(BaseModel):
    """A single file the (simulated) client has uploaded."""
    id: str
    session_id: str
    filename: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    # Populated by the agent after classification
    detected_type: Optional[str] = None      # which checklist key this looks like
    confidence: Optional[float] = None
    extracted_summary: Optional[str] = None  # short human-readable summary of what was found
    flag_reason: Optional[str] = None        # e.g. "expired", "wrong document type", "illegible"


class ChecklistItemState(BaseModel):
    """Live status of one checklist item for a session — what the dashboard renders."""
    key: str
    label: str
    required: bool
    status: DocumentStatus
    matched_document_id: Optional[str] = None
    flag_reason: Optional[str] = None


class SessionStateResponse(BaseModel):
    """Full snapshot returned to the frontend dashboard."""
    session: ClientSession
    checklist: list[ChecklistItemState]
    completion_pct: float
    followup_message: Optional[str] = None


class ClassifyResult(BaseModel):
    """What the classification LLM call returns for one document."""
    detected_type: Optional[str]
    confidence: float
    summary: str
    is_valid: bool
    flag_reason: Optional[str] = None
