# Accounting Client Onboarding Agent

An AI agent that automates the manual part of onboarding a new accounting
client: collecting documents, checking them against a checklist, and
following up on whatever's missing — while leaving the actual accounting
judgment to the accountant.

## What it does

1. A firm defines a checklist for a client type (e.g. new business
   bookkeeping onboarding needs an EIN letter, formation docs, a prior-year
   return, bank statements, a voided check).
2. A client uploads documents.
3. The agent reads each document, figures out what it is, and matches it
   to the right checklist item — flagging anything that's the wrong
   document, expired, or otherwise not valid to accept.
4. The dashboard shows live status: received, needs review, or missing.
5. On demand, the agent drafts a follow-up message naming exactly what's
   still needed — ready to send, not a generic template.

## Tech stack

- **FastAPI** — backend API
- **LangGraph** — orchestrates the classification pipeline
  (classify → match to checklist → validate)
- **Google Gemini** (via LangChain) — document classification and
  follow-up drafting
- **pdfplumber** — extracts text from uploaded PDFs
- Plain HTML/CSS/JS frontend, no build step, served directly by FastAPI

## Running it locally

\`\`\`bash
cd backend
cp .env.example .env        # add your GEMINI_API_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload
\`\`\`

Open `http://127.0.0.1:8000/app/` for the dashboard.
Open `http://127.0.0.1:8000/docs` for the raw API.

## Project structure

\`\`\`
  app/
    main.py                 FastAPI app
    schema/            
        models.py            Data models
    helper/        
        checklists.py        Checklist definitions per client type
        extraction.py        PDF text extraction
    memory/                 
        store.py               Session/document storage
    agent/
      graph.py              LangGraph pipeline
      nodes.py               Classification steps
      llm.py                   Gemini calls
      followup.py               Follow-up message logic
    api_routers/
      sessions.py, documents.py, followup.py    API endpoints
    static/
      index.html            Dashboard
    storage/         
        schema.sql            Supabase schema (for future persistence)
  requirements.txt
\`\`\`

## Status

Working demo. Currently uses in-memory storage (resets on restart) —
`schema.sql` is ready for wiring in real Supabase persistence when needed.
Document intake and follow-up sending are both manually triggered right
now; connecting them to a real inbox or client portal is the natural next
step for a production deployment.