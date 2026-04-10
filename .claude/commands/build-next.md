# /build-next

Tell me exactly what to build next in QRTifact and give me the complete file content to write.

Read the current state of the project by scanning `app/` to see what files exist and what's still missing.

Then determine the next logical piece to build based on this priority order:

1. **Infrastructure first** (pyproject.toml, .env.example, docker-compose.yml, Dockerfile, nginx.conf, alembic.ini)
2. **Core** (config.py, database.py, security.py, exceptions.py, dependencies.py)
3. **Models** (base.py, then each model file, then models/__init__.py)
4. **Schemas** (one domain at a time: auth → exhibit → billing → etc.)
5. **Services** (one domain at a time, matching schemas)
6. **Routes** (one router at a time, matching services)
7. **main.py** (wire all routers)
8. **Celery tasks** (celery_app.py → qr_tasks → email_tasks → audio_tasks)
9. **Migrations** (migrations/env.py)
10. **Tests** (conftest.py → auth tests → exhibit tests)
11. **CI/CD** (.github/workflows/ci-cd.yml)

For the identified next file:
- State clearly: "Next file to create: `path/to/file.py`"
- Provide the COMPLETE file content — production-quality, no placeholders, fully async
- Follow all rules in CLAUDE.md
- After providing the content, say: "Write this file, then run `/build-next` again for the next one."

This creates a build loop where each `/build-next` gives one complete file to write.
