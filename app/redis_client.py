from redis import Redis, ConnectionPool


_pool = ConnectionPool(
    host="redis",
    port=6379,
    db=0,
    max_connections=50,
    decode_responses=True,
    socket_timeout=5,
    socket_connect_timeout=5,
)


def get_redis_client() -> Redis:
    client = Redis(connection_pool=_pool)
    return client