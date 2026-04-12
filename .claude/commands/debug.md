# /debug

Help me debug an issue in QRTifact.

Ask the user: "What's the error or unexpected behavior? Paste the error message, traceback, or describe what's wrong."

Then:

## Step 1 — Identify the layer
Based on the error, determine which layer it's in:
- **Import error / startup crash** → check main.py router registration, circular imports, missing __init__.py
- **422 Unprocessable Entity** → Pydantic schema mismatch — check request schema field names and types
- **500 Internal Server Error** → service logic error — check the traceback
- **SQLAlchemy error** → check async usage, missing await, wrong session type
- **Alembic error** → check env.py imports, migration state
- **Celery error** → check task registration, broker connection

## Step 2 — Read relevant files
Read the specific files involved in the error. Don't read everything — only what the traceback points to.

## Step 3 — Root cause
State the root cause clearly in one sentence.

## Step 4 — Fix
Show the user EXACTLY what to change:
- File path
- Old code (if replacing)
- New code

## Common QRTifact-specific issues to check:
- `MissingGreenlet` error → using sync SQLAlchemy in async context, or missing `await`
- `DetachedInstanceError` → accessing relationship after session closed — add `lazy="selectin"` or use `selectinload()`
- `greenlet_spawn` error → same as above
- `Task/model not found in Celery` → missing `include=["app.tasks.xxx"]` in Celery config
- `alembic can't detect changes` → models not imported in `migrations/env.py`
- `401 on public route` → accidentally added auth dependency
- `CORS error` → add origin to `allow_origins` in `main.py`

Guide the user to fix the issue, don't fix it yourself unless asked.
