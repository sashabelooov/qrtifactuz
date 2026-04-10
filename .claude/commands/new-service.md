# /new-service

Guide me through adding a new service method or a new service file to QRTifact.

Ask the user:
1. Which service file? (existing one like `auth_service.py`, or new one?)
2. What should the method do?

Then navigate:

## Step 1 — Service method signature
Show the method signature with correct types:
```python
async def method_name(
    self,
    db: AsyncSession,
    # ... params
) -> ReturnType:
```

## Step 2 — Query pattern
Show the correct SQLAlchemy 2.0 async pattern for the operation:

**SELECT one:**
```python
result = await db.execute(select(Model).where(Model.id == id))
obj = result.scalar_one_or_none()
if not obj:
    raise NotFoundException("Model not found")
```

**SELECT many:**
```python
result = await db.execute(select(Model).where(...).order_by(Model.created_at.desc()))
return result.scalars().all()
```

**INSERT:**
```python
obj = Model(**data)
db.add(obj)
await db.commit()
await db.refresh(obj)
return obj
```

**Atomic UPDATE (counters):**
```python
await db.execute(
    update(Model)
    .where(Model.id == id)
    .values(count_field=Model.count_field + 1)
)
await db.commit()
```

**DELETE:**
```python
await db.execute(delete(Model).where(Model.id == id))
await db.commit()
```

## Step 3 — Error handling
Remind to use only:
- `NotFoundException` — resource doesn't exist
- `ForbiddenException` — user doesn't have permission
- `BadRequestException` — invalid input / business rule violation
- `InsufficientScansException` — no scan credits left
- `UnauthorizedException` — not authenticated

## Step 4 — Return type
Remind: services should return ORM objects or simple dicts/dataclasses. Never return raw `Row` objects. The route will serialize using a Pydantic schema.

After each step, wait for confirmation.
