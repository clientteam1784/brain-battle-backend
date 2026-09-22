"""Add team PIN and batch-submission counters."""

import secrets
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260922_02"
down_revision: str | Sequence[str] | None = "20260911_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("team", sa.Column("pin", sa.String(length=6), nullable=True))
    op.add_column(
        "team",
        sa.Column("submission_round", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "answer",
        sa.Column("wrong_count", sa.Integer(), server_default="0", nullable=False),
    )

    connection = op.get_bind()
    team = sa.table("team", sa.column("id", sa.BigInteger()), sa.column("pin", sa.String(6)))
    existing_pins: set[str] = set()
    for team_id in connection.execute(sa.select(team.c.id)).scalars():
        while True:
            pin = str(100000 + secrets.randbelow(900000))
            if pin not in existing_pins:
                existing_pins.add(pin)
                break
        connection.execute(sa.update(team).where(team.c.id == team_id).values(pin=pin))

    answer = sa.table(
        "answer",
        sa.column("correct", sa.Boolean()),
        sa.column("submit_count", sa.Integer()),
        sa.column("wrong_count", sa.Integer()),
    )
    connection.execute(
        sa.update(answer).values(
            wrong_count=sa.case(
                (
                    answer.c.correct.is_(True) & (answer.c.submit_count > 0),
                    answer.c.submit_count - 1,
                ),
                (answer.c.correct.is_(True), 0),
                else_=answer.c.submit_count,
            )
        )
    )

    with op.batch_alter_table("team") as batch_op:
        batch_op.alter_column(
            "pin",
            existing_type=sa.String(length=6),
            nullable=False,
        )
        batch_op.create_unique_constraint("uq_team_pin", ["pin"])


def downgrade() -> None:
    with op.batch_alter_table("team") as batch_op:
        batch_op.drop_constraint("uq_team_pin", type_="unique")
    op.drop_column("answer", "wrong_count")
    op.drop_column("team", "submission_round")
    op.drop_column("team", "pin")
