from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from  api_routers import documents, followup, sessions

app = FastAPI(
    title="Accounting Client Onboarding Agent (Demo)",
    description=(
        "Demo agent: a client uploads documents, the agent classifies them "
        "against a checklist, flags what's missing or wrong, and drafts a "
        "follow-up message — human review stays in the loop for anything "
        "that needs judgment."
    ),
    version="0.1.0",
)

# Wide-open CORS for the demo frontend; tighten before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions.router)
app.include_router(documents.router)
app.include_router(followup.router)

# Serves the dashboard at /app/ — index.html lives in app/static/.
# Mounted AFTER the API routers on purpose: FastAPI matches routes in the
# order they're added, so /sessions etc. above still resolve to the API,
# not this static mount.
app.mount("/app", StaticFiles(directory="static", html=True), name="frontend")


@app.get("/")
def health_check():
    return RedirectResponse(url="/app/")