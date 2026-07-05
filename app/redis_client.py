from redis import Redis, ConnectionPool


_pool = ConnectionPool(
    host="redis",
    port=6379,
    db=0,
    max_connections=2,
    decode_responses=False,
)


def get_redis_client() -> Redis:
    client = Redis(connection_pool=_pool)
    return client
