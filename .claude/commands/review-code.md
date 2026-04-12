# /review-code

Review the code the user just wrote against QRTifact's architecture rules.

Read the file(s) the user has open or recently modified.

Check each of the following and report issues clearly:

## Architecture checks
- [ ] Routes only call services (no direct DB queries in routes)
- [ ] Services handle all business logic and raise AppException subclasses
- [ ] No raw ORM models returned from routes (must go through Pydantic schema)
- [ ] No `hashed_password`, `google_id`, or internal fields in response schemas

## Async checks
- [ ] All DB calls use `await`
- [ ] Session type is `AsyncSession`, not `Session`
- [ ] No sync SQLAlchemy calls (no `.query()`, no lazy relationship access)

## Counter/atomic operation checks
- [ ] Counters (views_count, listens_count, scans_left) use `UPDATE ... SET col = col + 1`
- [ ] No read-then-write pattern for counters

## Error handling checks
- [ ] Uses only exceptions from `app/core/exceptions.py`
- [ ] No bare `raise Exception(...)` or `HTTPException(...)` in services

## Schema checks
- [ ] Pydantic v2 syntax (`model_config = ConfigDict(from_attributes=True)`)
- [ ] Request schemas have proper validators
- [ ] Response schemas don't expose sensitive fields

## Security checks
- [ ] Admin routes use `Depends(get_current_admin)`
- [ ] Auth-required routes use `Depends(get_current_user)`
- [ ] No hardcoded secrets or credentials

## Webhook safety (if applicable)
- [ ] Raw payload saved to PaymentWebhookEvent BEFORE processing

For each issue found, show:
- The problematic line(s)
- Why it's wrong
- The corrected version

If no issues found, say: "Looks good — follows all QRTifact architecture rules."
