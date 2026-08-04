import os

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    MetaData,
    Table,
    Text,
    create_engine,
    func,
    insert,
    select,
    update,
)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is required")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
metadata = MetaData()

requests_table = Table(
    "requests",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("customer_name", Text, nullable=False),
    Column("customer_phone", Text, nullable=False),
    Column("customer_email", Text, nullable=True),
    Column("message", Text, nullable=False),
    Column("status", Text, nullable=False, server_default="new"),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
)


def init_database() -> None:
    metadata.create_all(engine)


def save_request(
    customer_name: str,
    customer_phone: str,
    customer_email: str,
    message: str,
) -> int:
    statement = (
        insert(requests_table)
        .values(
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            message=message,
        )
        .returning(requests_table.c.id)
    )

    with engine.begin() as connection:
        return connection.execute(statement).scalar_one()


def get_all_requests() -> list[dict]:
    statement = select(requests_table).order_by(requests_table.c.id.desc())

    with engine.connect() as connection:
        rows = connection.execute(statement).mappings().all()

    return [dict(row) for row in rows]


def get_request_by_id(request_id: int) -> dict | None:
    statement = select(requests_table).where(requests_table.c.id == request_id)

    with engine.connect() as connection:
        row = connection.execute(statement).mappings().one_or_none()

    return dict(row) if row is not None else None


def update_request_status(request_id: int, status: str) -> int:
    statement = (
        update(requests_table)
        .where(requests_table.c.id == request_id)
        .values(status=status)
    )

    with engine.begin() as connection:
        result = connection.execute(statement)
        updated_rows = result.rowcount

    return updated_rows
