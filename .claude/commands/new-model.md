# /new-model

Guide me step-by-step through adding a new SQLAlchemy model to QRTifact.

Ask the user: what is the model name and what domain does it belong to?

Then navigate them through each step:

## Step 1 — Create the model file
File: `app/models/{name}.py`

Provide the exact template:
```python
from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base

class ModelName(Base):
    __tablename__ = "table_name"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    # ... fields
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

Rules to remind:
- Use `Mapped[T]` and `mapped_column()` (SQLAlchemy 2.0 style)
- FK columns: `mapped_column(ForeignKey("other_table.id"), index=True)`
- Nullable fields: `Mapped[str | None] = mapped_column(..., nullable=True)`
- Relationships: `relationship("OtherModel", lazy="selectin")`
- Enums: define Python enum class first, then `Mapped[MyEnum] = mapped_column(SAEnum(MyEnum))`

## Step 2 — Register in models/__init__.py
Tell them to add: `from .{name} import ModelName` to `app/models/__init__.py`

## Step 3 — Verify alembic env.py imports it
Check that `migrations/env.py` imports from `app.models` so autogenerate picks it up.

## Step 4 — Generate and run migration
```bash
docker compose exec api uv run alembic revision --autogenerate -m "add {model_name} table"
docker compose exec api uv run alembic upgrade head
```

## Step 5 — Relationships in related models
Ask: "Does any existing model need a back-reference to this new model?"
If yes, show them exactly what `relationship()` to add.

After each step, wait for the user to confirm before proceeding.
