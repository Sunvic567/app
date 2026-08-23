"""
Thin wrapper around Gemini via LangChain, so the rest of the agent code
doesn't care which model/provider is behind it. The rest of the graph
only depends on the two function signatures below (classify_document,
draft_followup) — swap providers again later by editing only this file.
"""
import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from schema.models import ClassifyResult

_classify_llm = None
_followup_llm = None

# Pick a specific dated model (e.g. "gemini-2.5-flash") instead of a
# "-latest" alias if you want classification behavior to stay stable
# between runs — check ai.google.dev for current model names.
MODEL_NAME = "gemini-flash-latest"


def _require_api_key() -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Copy .env.example to .env "
            "and add your key before running the agent."
        )
    return api_key


def _get_classify_llm():
    global _classify_llm
    if _classify_llm is None:
        base_llm = ChatGoogleGenerativeAI(model=MODEL_NAME, google_api_key=_require_api_key())
        _classify_llm = base_llm.with_structured_output(ClassifyResult, method="json_schema")
    return _classify_llm


def _get_followup_llm():
    global _followup_llm
    if _followup_llm is None:
        _followup_llm = ChatGoogleGenerativeAI(model=MODEL_NAME, google_api_key=_require_api_key())
    return _followup_llm


def _message_text(content) -> str:
    """
    langchain_google_genai sometimes returns response.content as a plain
    string, and sometimes as a list of content parts. This normalizes
    either shape into one plain string.
    """
    if isinstance(content, list):
        return "".join(
            part if isinstance(part, str) else part.get("text", "")
            for part in content
        )
    return content


CLASSIFY_SYSTEM_PROMPT = """You are a document classification assistant for an \
accounting firm's client onboarding process. You will be given the extracted \
text of an uploaded document and a list of document types the firm is \
expecting from a new client.

Your job:
1. Decide which expected document type (if any) this document matches.
2. Rate your confidence (0.0-1.0).
3. Write a one-sentence summary of what the document actually is/contains.
4. Decide if it's valid to accept (is_valid) — flag it if it looks expired, \
illegible, incomplete, or clearly the wrong document type despite a partial match.

If there's no match, set detected_type to null and is_valid to false with an \
explanatory flag_reason."""


def classify_document(extracted_text: str, checklist_items: list[dict]) -> dict:
    """
    Calls the LLM to classify one document's extracted text against the
    checklist. Returns a dict matching ClassifyResult's fields.
    """
    llm = _get_classify_llm()

    checklist_desc = "\n".join(
        f"- key: \"{item['key']}\" | {item['label']}: {item['description']}"
        for item in checklist_items
    )

    user_prompt = f"""Expected document types for this client:
{checklist_desc}

--- Extracted document text (may be truncated) ---
{extracted_text[:6000]}
--- end of document text ---

Classify this document."""

    result: ClassifyResult = llm.invoke(
        [
            SystemMessage(content=CLASSIFY_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )
    return result.model_dump()


FOLLOWUP_SYSTEM_PROMPT = """You draft short, specific follow-up messages for an \
accounting firm to send to a client during onboarding. The message should:
- Name exactly which documents are still missing or need to be redone, and why.
- Sound like it's from a helpful staff member, not a form letter.
- Be concise — 4-8 sentences.
- Never invent a reason a document was flagged beyond what you're told.
- Skip pleasantries and small talk (no "I hope you're having a great week,"
  no "hope all is well") — get straight to what's needed.
- Stay matter-of-fact and professional. Do not use enthusiastic or
  salesy language like "excited to work with you" — this is a routine
  operational update, not a sales message."""


def draft_followup(client_name: str, missing_items: list[str], flagged_items: list[dict]) -> str:
    """
    missing_items: list of human-readable labels for checklist items with no upload yet.
    flagged_items: list of {"label": str, "reason": str} for uploads that need to be redone.
    """
    llm = _get_followup_llm()

    parts = []
    if missing_items:
        parts.append("Still missing entirely:\n" + "\n".join(f"- {m}" for m in missing_items))
    if flagged_items:
        flagged_desc = "\n".join(f"- {f['label']}: {f['reason']}" for f in flagged_items)
        parts.append("Received but needs attention:\n" + flagged_desc)

    user_prompt = f"""Client name: {client_name}

{chr(10).join(parts)}

Draft the follow-up message."""

    response = llm.invoke(
        [
            SystemMessage(content=FOLLOWUP_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )
    return _message_text(response.content).strip()