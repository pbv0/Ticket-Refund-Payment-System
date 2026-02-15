import os
import uuid
import asyncio
import logging
from databricks.sdk import WorkspaceClient
import psycopg
from psycopg_pool import ConnectionPool

logger = logging.getLogger(__name__)

_pool = None


def _get_instance_name() -> str:
    """Return the Lakebase instance name for credential generation.

    Uses LAKEBASE_INSTANCE_NAME if set, otherwise falls back to PGAPPNAME
    (which Databricks Apps sets to the app name). Override with
    LAKEBASE_INSTANCE_NAME if your instance name differs from the app name.
    """
    name = os.environ.get("LAKEBASE_INSTANCE_NAME") or os.environ.get("PGAPPNAME")
    if not name:
        raise RuntimeError(
            "Cannot determine Lakebase instance name. "
            "Set LAKEBASE_INSTANCE_NAME in your .env file or app.yaml."
        )
    return name


class RotatingTokenConnection(psycopg.Connection):
    """psycopg Connection subclass that fetches a fresh Databricks token on each connect."""

    @classmethod
    def connect(cls, conninfo: str = "", **kwargs):
        w = WorkspaceClient()
        kwargs["password"] = w.database.generate_database_credential(
            request_id=str(uuid.uuid4()),
            instance_names=[_get_instance_name()],
        ).token
        kwargs.setdefault("sslmode", "require")
        return super().connect(conninfo, **kwargs)


def get_pool() -> ConnectionPool:
    """Return (and lazily create) the shared connection pool.

    Expects PG* environment variables (PGHOST, PGDATABASE, PGPORT, etc.)
    to be set — either manually for local development or automatically by
    Databricks Apps when a Lakebase database resource is attached.
    """
    global _pool
    if _pool is None:
        if not os.environ.get("PGHOST"):
            raise RuntimeError(
                "PGHOST environment variable is not set. "
                "Add a Lakebase database instance as a resource to your Databricks App. "
                "See: https://docs.databricks.com/aws/en/dev-tools/databricks-apps/lakebase"
            )
        if not os.environ.get("PGUSER"):
            w = WorkspaceClient()
            os.environ["PGUSER"] = w.current_user.me().user_name
        _pool = ConnectionPool(
            conninfo="",
            connection_class=RotatingTokenConnection,
            min_size=1,
            max_size=5,
            open=True,
        )
    return _pool


def ensure_schema() -> None:
    """Create application tables if they do not already exist."""
    pool = get_pool()
    ddl = """
    CREATE TABLE IF NOT EXISTS help_ticket (
        ticket_id TEXT,
        customer_id TEXT,
        subject TEXT,
        status TEXT,
        created_at TIMESTAMP,
        resolved_at TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS refund_requests (
        refund_id TEXT,
        ticket_id TEXT,
        payment_id TEXT,
        sku TEXT,
        request_date TIMESTAMP,
        approved BOOLEAN,
        approval_date TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS stripe_payments (
        payment_id TEXT,
        customer_id TEXT,
        amount_cents INTEGER,
        currency TEXT,
        payment_status TEXT,
        payment_date TIMESTAMP
    );
    """
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)
    logger.info("Database schema verified — tables are ready.")


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