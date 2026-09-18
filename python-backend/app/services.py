import secrets
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import DomainError
from app.models import Answer, Question, Room, Student, Team


def create_question(
    session: Session,
    question_number: int,
    answer: str,
    max_submit_count: int,
) -> Question:
    question = Question(
        question_number=question_number,
        answer=answer,
        max_submit_count=max_submit_count,
    )
    session.add(question)
    try:
        session.flush()
    except IntegrityError as exc:
        raise DomainError("이미 존재하는 문제 번호입니다.") from exc
    return question


def list_questions(session: Session) -> list[Question]:
    return list(session.scalars(select(Question).order_by(Question.question_number)))


def update_question(
    session: Session,
    question_id: int,
    question_number: int,
    answer: str,
    max_submit_count: int,
) -> Question:
    question = session.get(Question, question_id)
    if question is None:
        raise DomainError("존재하지 않는 문제입니다.")
    question.question_number = question_number
    question.answer = answer
    question.max_submit_count = max_submit_count
    try:
        session.flush()
    except IntegrityError as exc:
        raise DomainError("이미 존재하는 문제 번호입니다.") from exc
    return question


def delete_question(session: Session, question_id: int) -> None:
    question = session.get(Question, question_id)
    if question is None:
        raise DomainError("존재하지 않는 문제입니다.")
    session.delete(question)


def create_room(session: Session) -> Room:
    for _ in range(20):
        pin = str(100000 + secrets.randbelow(900000))
        exists = session.scalar(select(Room.id).where(Room.pin == pin))
        if exists is None:
            room = Room(pin=pin)
            session.add(room)
            session.flush()
            return room
    raise DomainError("방 PIN을 생성하지 못했습니다. 다시 시도해주세요.", 503)


def start_room(session: Session, room_id: int) -> Room:
    room = session.get(Room, room_id)
    if room is None:
        raise DomainError("존재하지 않는 방입니다.")
    room.started = True
    session.flush()
    return room


def join_room(session: Session, pin: str, team_name: str) -> Team:
    room = session.scalar(select(Room).where(Room.pin == pin))
    if room is None:
        raise DomainError("존재하지 않는 pin입니다.")
    existing = session.scalar(
        select(Team.id).where(Team.room_id == room.id, Team.name == team_name)
    )
    if existing is not None:
        raise DomainError("이미 존재하는 모둠 이름입니다.")
    team = Team(name=team_name, room=room)
    session.add(team)
    try:
        session.flush()
    except IntegrityError as exc:
        raise DomainError("이미 존재하는 모둠 이름입니다.") from exc
    return team


def join_team(session: Session, team_id: int, student_number: str) -> Student:
    student_number = student_number.strip()
    if not student_number:
        raise DomainError("학번은 필수입니다.")
    team = session.get(Team, team_id)
    if team is None:
        raise DomainError("존재하지 않는 모둠입니다.")
    existing = session.scalar(
        select(Student.id).where(
            Student.student_number == student_number,
            Student.team_id == team_id,
        )
    )
    if existing is not None:
        raise DomainError("이미 해당 모둠에 등록된 학번입니다.")
    student = Student(student_number=student_number, team=team)
    session.add(student)
    try:
        session.flush()
    except IntegrityError as exc:
        raise DomainError("이미 해당 모둠에 등록된 학번입니다.") from exc
    return student


def submit_answer(
    session: Session,
    team_id: int,
    question_id: int,
    submitted_answer: str,
) -> Answer:
    team = session.scalar(select(Team).where(Team.id == team_id).with_for_update())
    if team is None:
        raise DomainError("존재하지 않는 모둠입니다.")
    if not team.room.started:
        raise DomainError("아직 게임이 시작되지 않았습니다.")
    if team.finished:
        raise DomainError("이미 모든 문제를 완료한 모둠입니다.")

    question = session.get(Question, question_id)
    if question is None:
        raise DomainError("존재하지 않는 문제입니다.")

    answer = session.scalar(
        select(Answer)
        .where(Answer.team_id == team_id, Answer.question_id == question_id)
        .with_for_update()
    )
    was_correct = answer is not None and answer.correct

    if answer is None:
        answer = Answer(
            team=team,
            question=question,
            submitted_answer=submitted_answer,
            submit_count=1,
        )
        session.add(answer)
    else:
        if answer.correct:
            raise DomainError("이미 정답을 맞힌 문제입니다.")
        if answer.submit_count >= question.max_submit_count:
            raise DomainError("답안 제출 횟수를 초과했습니다.")
        answer.submitted_answer = submitted_answer
        answer.submit_count += 1
        answer.modify_count += 1

    answer.correct = question.answer.casefold() == submitted_answer.strip().casefold()
    if not was_correct and answer.correct:
        team.current_count += 1
        total_questions = session.scalar(select(func.count(Question.id))) or 0
        if team.current_count >= total_questions and not team.finished:
            team.finished = True
            team.finished_at = datetime.now()

    try:
        session.flush()
    except IntegrityError as exc:
        raise DomainError("동일한 답안이 동시에 제출되었습니다. 다시 시도해주세요.", 409) from exc
    return answer


def get_ranking(session: Session, room_id: int) -> list[Team]:
    room_exists = session.scalar(select(Room.id).where(Room.id == room_id))
    if room_exists is None:
        raise DomainError("존재하지 않는 방입니다.")
    return list(
        session.scalars(
            select(Team)
            .where(Team.room_id == room_id)
            .order_by(
                Team.finished.desc(),
                Team.finished_at.asc(),
                Team.current_count.desc(),
                Team.id.asc(),
            )
        )
    )
