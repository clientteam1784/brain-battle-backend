from datetime import datetime
from typing import Annotated

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

id_type = BigInteger().with_variant(Integer, "sqlite")
PrimaryKey = Annotated[int, mapped_column(id_type, primary_key=True, autoincrement=True)]


class Room(Base):
    __tablename__ = "room"
    __table_args__ = (UniqueConstraint("pin", name="uq_room_pin"),)

    id: Mapped[PrimaryKey]
    pin: Mapped[str] = mapped_column(String(6), nullable=False)
    started: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    teams: Mapped[list["Team"]] = relationship(back_populates="room")


class Team(Base):
    __tablename__ = "team"
    __table_args__ = (
        UniqueConstraint("room_id", "name", name="uq_team_room_name"),
        UniqueConstraint("pin", name="uq_team_pin"),
    )

    id: Mapped[PrimaryKey]
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    pin: Mapped[str] = mapped_column(String(6), nullable=False)
    current_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    submission_round: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    finished: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    room_id: Mapped[int] = mapped_column(
        id_type,
        ForeignKey("room.id", ondelete="CASCADE"),
        nullable=False,
    )

    room: Mapped[Room] = relationship(back_populates="teams")
    students: Mapped[list["Student"]] = relationship(back_populates="team")
    answers: Mapped[list["Answer"]] = relationship(back_populates="team")


class Student(Base):
    __tablename__ = "student"
    __table_args__ = (UniqueConstraint("team_id", "student_number", name="uq_student_team_number"),)

    id: Mapped[PrimaryKey]
    student_number: Mapped[str] = mapped_column(String(255), nullable=False)
    team_id: Mapped[int] = mapped_column(
        id_type,
        ForeignKey("team.id", ondelete="CASCADE"),
        nullable=False,
    )

    team: Mapped[Team] = relationship(back_populates="students")


class Question(Base):
    __tablename__ = "question"
    __table_args__ = (UniqueConstraint("question_number", name="uq_question_number"),)

    id: Mapped[PrimaryKey]
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    answer: Mapped[str] = mapped_column(String(255), nullable=False)
    max_submit_count: Mapped[int] = mapped_column(Integer, nullable=False)

    answers: Mapped[list["Answer"]] = relationship(back_populates="question")


class Answer(Base):
    __tablename__ = "answer"
    __table_args__ = (UniqueConstraint("team_id", "question_id", name="uq_answer_team_question"),)

    id: Mapped[PrimaryKey]
    team_id: Mapped[int] = mapped_column(
        id_type,
        ForeignKey("team.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id: Mapped[int] = mapped_column(
        id_type,
        ForeignKey("question.id", ondelete="CASCADE"),
        nullable=False,
    )
    submitted_answer: Mapped[str] = mapped_column(String(255), nullable=False)
    correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    submit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    modify_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    wrong_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    team: Mapped[Team] = relationship(back_populates="answers")
    question: Mapped[Question] = relationship(back_populates="answers")
