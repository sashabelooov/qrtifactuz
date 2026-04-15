import random
import redis.asyncio as aioredis
from app.core.config import settings


def generate_otp() -> str:
    return str(random.randint(100000, 999999))


REDIS_OTP_TTL = 600  # 10 minutes


async def get_redis():
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


async def save_otp(user_id: str, otp: str) -> None:
    r = await get_redis()
    await r.set(f"otp:{user_id}", otp, ex=REDIS_OTP_TTL)
    await r.aclose()


async def verify_otp(user_id: str, otp: str) -> bool:
    r = await get_redis()
    stored = await r.get(f"otp:{user_id}")
    await r.aclose()
    if not stored or stored != otp:
        return False
    return True


async def delete_otp(user_id: str) -> None:
    r = await get_redis()
    await r.delete(f"otp:{user_id}")
    await r.aclose()
