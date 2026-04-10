# /new-endpoint

Guide me step-by-step through adding a new API endpoint to the QRTifact project.

Ask the user for:
1. The HTTP method and path (e.g. `GET /api/v1/exhibits/{id}/media`)
2. Whether it's public, auth-required, or admin-only
3. What it does (brief description)

Then navigate them through each file they need to create or edit, in this exact order:

## Step 1 — Schema
Tell them exactly what Pydantic schema(s) to add in `app/schemas/`.
- Show the Request schema (if POST/PUT/PATCH)
- Show the Response schema
- Remind them: `model_config = ConfigDict(from_attributes=True)`

## Step 2 — Service method
Tell them exactly what async method to add to the relevant service in `app/services/`.
- Show the full method signature with type hints
- Show the SQLAlchemy query (use `select()`, `update()`, etc.)
- Remind them: atomic updates for counters, raise AppException subclasses for errors

## Step 3 — Route
Tell them exactly what to add to the relevant router in `app/api/v1/`.
- Show the decorator (`@router.get(...)` etc.) with `response_model`
- Show the dependency injection (`Depends(get_db)`, `Depends(get_current_user)` etc.)
- Route body: call service, return response schema

## Step 4 — Registration check
Ask: "Is this router already registered in `app/main.py`?"
If no, tell them exactly where to add `app.include_router(...)`.

## Step 5 — Migration check
Ask: "Did you add any new model fields?" If yes, remind them:
```bash
docker compose exec api uv run alembic revision --autogenerate -m "describe change"
docker compose exec api uv run alembic upgrade head
```

After each step, wait for the user to confirm before moving to the next step.
