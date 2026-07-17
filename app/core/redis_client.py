import os
import redis

redis_url = os.getenv("REDIS_URL")

if redis_url:
    # Production (e.g. Upstash) — full connection URL, handles TLS automatically
    redis_client = redis.from_url(redis_url, decode_responses=True)
# for local docker compose service
else:
    redis_client = redis.Redis(host='redis',  
                        port=6379,
                        decode_responses=True,
                        socket_connect_timeout=5
                        )

def get_redis_client() -> redis.Redis:
    return redis_client