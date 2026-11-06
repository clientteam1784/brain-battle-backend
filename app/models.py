from datetime import datetime
from typing import Annotated

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# 운영 DB에서는 큰 정수 ID를 쓰고, SQLite 테스트에서는 호환되는 INTEGER를 씁니다.
id_type = BigInteger().with_variant(Integer, "sqlite")
PrimaryKey = Annotated[int, mapped_column(id_type, primary_key=True, autoincrement=True)]


# 한 번의 게임 공간입니다. PIN은 참가 코드이고 started는 게임 시작 여부입니다.
# 한 번의 게임 세션을 나타냅니다. teams 관계로 이 방의 모둠을 탐색할 수 있습니다.
class Room(Base):
    __tablename__ = "room"
    __table_args__ = (UniqueConstraint("pin", name="uq_room_pin"),)

    id: Mapped[PrimaryKey]
    pin: Mapped[str] = mapped_column(String(6), nullable=False)
    started: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    teams: Mapped[list["Team"]] = relationship(back_populates="room")


# 방 안의 모둠과 진행 상태를 저장합니다. PIN은 학생 로그인에 사용됩니다.
# 방에 속한 모둠과 점수, 제출 회차, 완료 시각을 저장합니다.
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


# 조별 학번을 저장합니다. 같은 조 안에서 학번은 중복될 수 없습니다.
# 학생의 학번과 소속 모둠을 저장합니다.
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


# 교사가 등록하는 문제와 정답, 허용 제출 횟수입니다.
# 문제 번호, 정답, 최대 제출 횟수를 저장합니다.
class Question(Base):
    __tablename__ = "question"
    __table_args__ = (UniqueConstraint("question_number", name="uq_question_number"),)

    id: Mapped[PrimaryKey]
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    answer: Mapped[str] = mapped_column(String(255), nullable=False)
    max_submit_count: Mapped[int] = mapped_column(Integer, nullable=False)

    answers: Mapped[list["Answer"]] = relationship(back_populates="question")


# 조가 문항에 제출한 최신 답과 채점/시도 횟수를 저장합니다.
# 모둠이 특정 문제에 낸 최신 답과 채점/시도 횟수를 저장합니다.
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
