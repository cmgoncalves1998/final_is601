# app/auth/redis.py
from app.core.config import get_settings

try:
    import aioredis
except (ImportError, ModuleNotFoundError):
    aioredis = None

settings = get_settings()

async def get_redis():
    if aioredis is None:
        return None
    if not hasattr(get_redis, "redis"):
        try:
            get_redis.redis = await aioredis.from_url(
                settings.REDIS_URL or "redis://localhost"
            )
        except Exception:
            get_redis.redis = None
    return get_redis.redis

async def add_to_blacklist(jti: str, exp: int):
    """Add a token's JTI to the blacklist"""
    redis = await get_redis()
    if redis is None:
        return
    await redis.set(f"blacklist:{jti}", "1", ex=exp)

async def is_blacklisted(jti: str) -> bool:
    """Check if a token's JTI is blacklisted"""
    redis = await get_redis()
    if redis is None:
        return False
    return bool(await redis.exists(f"blacklist:{jti}"))
