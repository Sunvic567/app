-- Supabase schema for the accounting onboarding agent.
-- Not wired in yet for the demo (app/store.py uses an in-memory store),
-- but this is the shape to migrate to once you want real persistence
-- or multi-user demos.

create table if not exists client_sessions (
    id uuid primary key default gen_random_uuid(),
    client_name text not null,
    checklist_type text not null,  -- matches ChecklistTemplateType values
    created_at timestamptz not null default now()
);

create table if not exists uploaded_documents (
    id uuid primary key default gen_random_uuid(),
    session_id uuid not null references client_sessions(id) on delete cascade,
    filename text not null,
    uploaded_at timestamptz not null default now(),

    detected_type text,
    confidence float,
    extracted_summary text,
    flag_reason text
);

create index if not exists idx_uploaded_documents_session
    on uploaded_documents (session_id);

-- If you later want checklist templates to be editable per firm rather
-- than hardcoded in app/checklists.py, this table shape would replace it:
create table if not exists checklist_templates (
    id uuid primary key default gen_random_uuid(),
    checklist_type text not null,
    key text not null,
    label text not null,
    description text not null,
    required boolean not null default true,
    unique (checklist_type, key)
);
