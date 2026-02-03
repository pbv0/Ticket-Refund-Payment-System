import uuid
import asyncio
import logging
from typing import Any, Optional
from databricks.sdk import WorkspaceClient
import psycopg
from psycopg_pool import ConnectionPool

_pool = None
_db_config = None
INSTANCE_NAME = "Practice1"
DATABASE = "databricks_postgres"


class RotatingTokenConnection(psycopg.Connection):
    @classmethod
    def connect(cls, conninfo: str = "", **kwargs):
        w = WorkspaceClient()
        instance_name = kwargs.pop("_instance_name", None)
        if instance_name:
            kwargs["password"] = w.database.generate_database_credential(
                request_id=str(uuid.uuid4()), instance_names=[instance_name]
            ).token
        kwargs.setdefault("sslmode", "require")
        return super().connect(conninfo, **kwargs)


def _get_config():
    global _db_config
    if _db_config is None:
        w = WorkspaceClient()
        instances = list(w.database.list_database_instances())
        target_instance = next(
            (i for i in instances if i.name == INSTANCE_NAME), instances[0]
        )
        _db_config = {
            "host": target_instance.read_write_dns,
            "user": w.current_user.me().user_name,
            "instance_name": target_instance.name,
        }
    return _db_config


def get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        config = _get_config()
        conninfo = f"host={config['host']} dbname={DATABASE} user={config['user']}"
        _pool = ConnectionPool(
            conninfo=conninfo,
            connection_class=RotatingTokenConnection,
            kwargs={"_instance_name": config["instance_name"]},
            min_size=1,
            max_size=5,
            open=True,
        )
    return _pool


def _execute_sync(
    sql: str,
    params: dict[str, str | int | float | bool | None] | tuple | None = None,
    fetch: str | None = None,
) -> list[tuple] | tuple | None:
    pool = get_pool()
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if fetch == "all":
                return cur.fetchall()
            elif fetch == "one":
                return cur.fetchone()
            else:
                return None


async def fetch_all(
    sql: str, params: dict[str, str | int | float | bool | None] | tuple | None = None
) -> list[tuple]:
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, _execute_sync, sql, params, "all")
    return result if result is not None else []


async def fetch_one(
    sql: str, params: dict[str, str | int | float | bool | None] | tuple | None = None
) -> tuple | None:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _execute_sync, sql, params, "one")


async def execute(
    sql: str, params: dict[str, str | int | float | bool | None] | tuple | None = None
) -> None:
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, _execute_sync, sql, params, None)