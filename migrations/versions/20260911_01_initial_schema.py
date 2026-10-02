"""Create the Brain Battle schema for a new database."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260911_01"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "question",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("question_number", sa.Integer(), nullable=False),
        sa.Column("answer", sa.String(length=255), nullable=False),
        sa.Column("max_submit_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("question_number", name="uq_question_number"),
    )
    op.create_table(
        "room",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("pin", sa.String(length=6), nullable=False),
        sa.Column("started", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("pin", name="uq_room_pin"),
    )
    op.create_table(
        "team",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("current_count", sa.Integer(), nullable=False),
        sa.Column("finished", sa.Boolean(), nullable=False),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("room_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["room_id"], ["room.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("room_id", "name", name="uq_team_room_name"),
    )
    op.create_table(
        "student",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("student_number", sa.String(length=255), nullable=False),
        sa.Column("team_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["team_id"], ["team.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("team_id", "student_number", name="uq_student_team_number"),
    )
    op.create_table(
        "answer",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("team_id", sa.BigInteger(), nullable=False),
        sa.Column("question_id", sa.BigInteger(), nullable=False),
        sa.Column("submitted_answer", sa.String(length=255), nullable=False),
        sa.Column("correct", sa.Boolean(), nullable=False),
        sa.Column("submit_count", sa.Integer(), nullable=False),
        sa.Column("modify_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["question.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["team.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("team_id", "question_id", name="uq_answer_team_question"),
    )


def downgrade() -> None:
    op.drop_table("answer")
    op.drop_table("student")
    op.drop_table("team")
    op.drop_table("room")
    op.drop_table("question")
