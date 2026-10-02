import secrets
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.exceptions import DomainError
from app.models import Answer, Question, Room, Student, Team
from app.schemas import AnswerStatus, BatchAnswerItem


def create_question(
    session: Session,
    question_number: int,
    answer: str,
    max_submit_count: int,
) -> Question:
    question = Question(
        question_number=question_number,
        answer=answer.strip(),
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
        raise DomainError("존재하지 않는 문제입니다.", 404, include_status=True)
    question.question_number = question_number
    question.answer = answer.strip()
    question.max_submit_count = max_submit_count
    try:
        session.flush()
    except IntegrityError as exc:
        raise DomainError("이미 존재하는 문제 번호입니다.") from exc
    return question


def delete_question(session: Session, question_id: int) -> None:
    question = session.get(Question, question_id)
    if question is None:
        raise DomainError("존재하지 않는 문제입니다.", 404, include_status=True)
    session.delete(question)


def _unique_pin(session: Session, model: type[Room] | type[Team], label: str) -> str:
    for _ in range(30):
        pin = str(100000 + secrets.randbelow(900000))
        if session.scalar(select(model.id).where(model.pin == pin)) is None:
            return pin
    raise DomainError(f"{label} PIN을 생성하지 못했습니다. 다시 시도해주세요.", 503)


def create_room(session: Session) -> Room:
    try:
        room = Room(pin=_unique_pin(session, Room, "방"))
        session.add(room)
        session.flush()
    except (DomainError, IntegrityError) as exc:
        raise DomainError("방 생성에 실패했습니다.", 500, include_status=True) from exc
    return room


def start_room(session: Session, room_id: int) -> Room:
    room = session.get(Room, room_id)
    if room is None:
        raise DomainError("존재하지 않는 방입니다.", 404, include_status=True)
    if room.started:
        raise DomainError("이미 시작된 게임입니다.", include_status=True)
    question_numbers = {question.question_number for question in list_questions(session)}
    if question_numbers != set(range(1, 11)):
        raise DomainError("게임 시작 전 1번부터 10번까지 문제를 등록해야 합니다.")
    room.started = True
    session.flush()
    return room


def create_team(session: Session, room_id: int, team_name: str) -> Team:
    room = session.get(Room, room_id)
    if room is None:
        raise DomainError("존재하지 않는 방입니다.", 404)
    existing = session.scalar(
        select(Team.id).where(Team.room_id == room.id, Team.name == team_name)
    )
    if existing is not None:
        raise DomainError("이미 존재하는 모둠 이름입니다.")
    team = Team(
        name=team_name,
        pin=_unique_pin(session, Team, "조"),
        room=room,
    )
    session.add(team)
    try:
        session.flush()
    except IntegrityError as exc:
        raise DomainError("이미 존재하는 모둠 이름 또는 PIN입니다.") from exc
    return team


def authenticate_student(session: Session, team_pin: str, student_number: str) -> Student:
    team = session.scalar(select(Team).where(Team.pin == team_pin))
    if team is None:
        raise DomainError("존재하지 않는 조 PIN입니다.", 401)
    student_number = student_number.strip()
    if not student_number:
        raise DomainError("학번은 필수입니다.")
    student = session.scalar(
        select(Student).where(
            Student.student_number == student_number,
            Student.team_id == team.id,
        )
    )
    if student is None:
        student = Student(student_number=student_number, team=team)
        session.add(student)
        try:
            session.flush()
        except IntegrityError as exc:
            raise DomainError("학생 등록 중 충돌이 발생했습니다.", 409) from exc
    return student


def join_team(session: Session, team_id: int, student_number: str) -> Student:
    team = session.get(Team, team_id)
    if team is None:
        raise DomainError("존재하지 않는 모둠입니다.", 404)
    return authenticate_student(session, team.pin, student_number)


def list_room_teams(session: Session, room_id: int) -> list[Team]:
    if session.get(Room, room_id) is None:
        raise DomainError("존재하지 않는 방입니다.", 404, include_status=True)
    return list(session.scalars(select(Team).where(Team.room_id == room_id).order_by(Team.id)))


def get_team(session: Session, team_id: int) -> Team:
    team = session.get(Team, team_id)
    if team is None:
        raise DomainError("존재하지 않는 모둠입니다.", 404)
    return team


def get_answer(session: Session, team_id: int, question_id: int) -> Answer:
    answer = session.scalar(
        select(Answer).where(Answer.team_id == team_id, Answer.question_id == question_id)
    )
    if answer is None:
        raise DomainError("존재하지 않는 답안입니다.", 404)
    return answer


def _answer_status(answer: Answer | None, question: Question) -> AnswerStatus:
    if answer is None:
        return AnswerStatus.UNSUBMITTED
    if answer.correct:
        return AnswerStatus.CORRECT
    if answer.submit_count >= question.max_submit_count:
        return AnswerStatus.EXHAUSTED
    return AnswerStatus.WRONG


def _grade_answer(
    session: Session,
    team: Team,
    question: Question,
    answer: Answer | None,
    submitted_answer: str,
) -> tuple[Answer, bool]:
    value = submitted_answer.strip()
    if not value:
        if answer is None:
            raise DomainError("미제출 답안은 저장하지 않습니다.")
        return answer, False
    if answer is not None and _answer_status(answer, question) in {
        AnswerStatus.CORRECT,
        AnswerStatus.EXHAUSTED,
    }:
        return answer, False

    if answer is None:
        answer = Answer(
            team=team,
            question=question,
            submitted_answer=value,
            submit_count=1,
            wrong_count=0,
        )
        session.add(answer)
    else:
        answer.submitted_answer = value
        answer.submit_count += 1
        answer.modify_count += 1

    answer.correct = question.answer.casefold() == value.casefold()
    if not answer.correct:
        answer.wrong_count += 1
    return answer, True


def _load_team_for_submission(session: Session, team_id: int) -> Team:
    team = session.scalar(select(Team).where(Team.id == team_id).with_for_update())
    if team is None:
        raise DomainError("존재하지 않는 모둠입니다.", 404)
    if not team.room.started:
        raise DomainError("아직 게임이 시작되지 않았습니다.")
    if team.finished:
        raise DomainError("이미 모든 문제를 완료한 모둠입니다.")
    return team


def submit_answer(
    session: Session,
    team_id: int,
    question_id: int,
    submitted_answer: str,
) -> Answer:
    team = _load_team_for_submission(session, team_id)
    question = session.get(Question, question_id)
    if question is None:
        raise DomainError("존재하지 않는 문제입니다.", 404)
    answer = session.scalar(
        select(Answer)
        .where(Answer.team_id == team_id, Answer.question_id == question_id)
        .with_for_update()
    )
    status = _answer_status(answer, question)
    if status == AnswerStatus.CORRECT:
        raise DomainError("이미 정답을 맞힌 문제입니다.")
    if status == AnswerStatus.EXHAUSTED:
        raise DomainError("답안 제출 횟수를 초과했습니다.")
    graded, _ = _grade_answer(session, team, question, answer, submitted_answer)
    session.flush()
    _refresh_team_completion(session, team)
    return graded


def _refresh_team_completion(session: Session, team: Team) -> None:
    questions = list_questions(session)
    answers = list(session.scalars(select(Answer).where(Answer.team_id == team.id)))
    team.current_count = sum(answer.correct for answer in answers)
    if questions and team.current_count == len(questions):
        team.finished = True
        team.finished_at = team.finished_at or datetime.now()


def submit_answer_batch(
    session: Session,
    team_id: int,
    submitted_items: list[BatchAnswerItem],
) -> tuple[dict, int]:
    team = _load_team_for_submission(session, team_id)
    questions = list_questions(session)
    question_by_id = {question.id: question for question in questions}
    submitted_by_id = {item.question_id: item.submitted_answer for item in submitted_items}
    unknown_ids = sorted(set(submitted_by_id) - set(question_by_id))
    if unknown_ids:
        raise DomainError(f"존재하지 않는 문제 ID가 포함되어 있습니다: {unknown_ids}")

    answers = {
        answer.question_id: answer
        for answer in session.scalars(
            select(Answer).where(Answer.team_id == team_id).with_for_update()
        )
    }
    graded_count = 0
    for question in questions:
        submitted = submitted_by_id.get(question.id)
        if submitted is None or not submitted.strip():
            continue
        answer, graded = _grade_answer(
            session,
            team,
            question,
            answers.get(question.id),
            submitted,
        )
        answers[question.id] = answer
        graded_count += int(graded)

    team.submission_round += 1
    try:
        session.flush()
    except IntegrityError as exc:
        raise DomainError("동일한 답안이 동시에 제출되었습니다. 다시 시도해주세요.", 409) from exc
    _refresh_team_completion(session, team)
    session.flush()
    return build_team_progress(session, team.id), graded_count


def build_team_progress(session: Session, team_id: int) -> dict:
    team = get_team(session, team_id)
    questions = list_questions(session)
    answers = {
        answer.question_id: answer
        for answer in session.scalars(select(Answer).where(Answer.team_id == team_id))
    }
    question_states = []
    rotation_ids = []
    for question in questions:
        answer = answers.get(question.id)
        status = _answer_status(answer, question)
        locked = status in {AnswerStatus.CORRECT, AnswerStatus.EXHAUSTED}
        if not locked:
            rotation_ids.append(question.id)
        submit_count = answer.submit_count if answer else 0
        question_states.append(
            {
                "questionId": question.id,
                "questionNumber": question.question_number,
                "status": status,
                "submittedAnswer": answer.submitted_answer if answer else None,
                "submitCount": submit_count,
                "wrongCount": answer.wrong_count if answer else 0,
                "maxSubmitCount": question.max_submit_count,
                "remainingAttempts": max(question.max_submit_count - submit_count, 0),
                "locked": locked,
            }
        )
    return {
        "teamId": team.id,
        "submissionRound": team.submission_round,
        "correctCount": team.current_count,
        "totalQuestions": len(questions),
        "finished": team.finished,
        "questions": question_states,
        "rotationQuestionIds": rotation_ids,
        "nextQuestionId": rotation_ids[0] if rotation_ids else None,
    }


def get_ranking(session: Session, room_id: int) -> list[Team]:
    room_exists = session.scalar(select(Room.id).where(Room.id == room_id))
    if room_exists is None:
        raise DomainError("존재하지 않는 방입니다.", 404)
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
