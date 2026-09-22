import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app import services
from app.auth import (
    CurrentPrincipal,
    Principal,
    StudentPrincipal,
    TeacherPrincipal,
    create_access_token,
)
from app.config import get_settings
from app.database import get_session
from app.exceptions import DomainError
from app.models import Team
from app.schemas import (
    AnswerResponse,
    AnswerSubmitRequest,
    AuthTokenResponse,
    BatchAnswerSubmitRequest,
    BatchAnswerSubmitResponse,
    QuestionRequest,
    QuestionResponse,
    RankingResponse,
    RoomResponse,
    StudentLoginRequest,
    StudentResponse,
    TeacherLoginRequest,
    TeamJoinRequest,
    TeamProgressResponse,
    TeamResponse,
)

router = APIRouter()
DbSession = Annotated[Session, Depends(get_session)]


def _require_own_team(principal: Principal, team_id: int) -> None:
    if principal.team_id != team_id:
        raise DomainError("다른 조의 정보에는 접근할 수 없습니다.", 403)


@router.post("/auth/teacher", response_model=AuthTokenResponse, tags=["auth"])
def login_teacher(request: TeacherLoginRequest) -> AuthTokenResponse:
    if not secrets.compare_digest(request.access_code, get_settings().teacher_access_code):
        raise DomainError("선생님 인증 코드가 올바르지 않습니다.", 401)
    principal = Principal(role="teacher")
    token, expires_in = create_access_token(principal)
    return AuthTokenResponse(
        accessToken=token,
        role=principal.role,
        expiresIn=expires_in,
    )


@router.post("/auth/student", response_model=AuthTokenResponse, tags=["auth"])
def login_student(request: StudentLoginRequest, session: DbSession) -> AuthTokenResponse:
    student = services.authenticate_student(
        session,
        request.team_pin,
        request.student_number,
    )
    principal = Principal(role="student", student_id=student.id, team_id=student.team_id)
    token, expires_in = create_access_token(principal)
    return AuthTokenResponse(
        accessToken=token,
        role=principal.role,
        expiresIn=expires_in,
        studentId=student.id,
        teamId=student.team_id,
    )


@router.post("/questions", response_model=QuestionResponse, tags=["questions"])
def create_question(
    request: QuestionRequest,
    session: DbSession,
    _: TeacherPrincipal,
) -> QuestionResponse:
    question = services.create_question(
        session,
        request.question_number,
        request.answer,
        request.max_submit_count,
    )
    return QuestionResponse.model_validate(question)


@router.get("/questions", response_model=list[QuestionResponse], tags=["questions"])
def get_questions(session: DbSession, _: CurrentPrincipal) -> list[QuestionResponse]:
    return [QuestionResponse.model_validate(item) for item in services.list_questions(session)]


@router.patch(
    "/questions/{question_id}",
    response_model=QuestionResponse,
    tags=["questions"],
)
def update_question(
    question_id: int,
    request: QuestionRequest,
    session: DbSession,
    _: TeacherPrincipal,
) -> QuestionResponse:
    question = services.update_question(
        session,
        question_id,
        request.question_number,
        request.answer,
        request.max_submit_count,
    )
    return QuestionResponse.model_validate(question)


@router.delete(
    "/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["questions"],
)
def delete_question(
    question_id: int,
    session: DbSession,
    _: TeacherPrincipal,
) -> Response:
    services.delete_question(session, question_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/rooms", response_model=RoomResponse, tags=["rooms"])
def create_room(session: DbSession, _: TeacherPrincipal) -> RoomResponse:
    return RoomResponse.model_validate(services.create_room(session))


@router.patch("/rooms/{room_id}/start", response_model=RoomResponse, tags=["rooms"])
def start_room(
    room_id: int,
    session: DbSession,
    _: TeacherPrincipal,
) -> RoomResponse:
    return RoomResponse.model_validate(services.start_room(session, room_id))


@router.post("/rooms/{room_id}/teams", response_model=TeamResponse, tags=["teams"])
def create_team(
    room_id: int,
    request: TeamJoinRequest,
    session: DbSession,
    _: TeacherPrincipal,
) -> TeamResponse:
    return TeamResponse.model_validate(services.create_team(session, room_id, request.team_name))


@router.post(
    "/rooms/by-pin/{pin}/teams",
    response_model=TeamResponse,
    tags=["teams"],
    deprecated=True,
)
def create_team_by_room_pin(
    pin: str,
    request: TeamJoinRequest,
    session: DbSession,
    _: TeacherPrincipal,
) -> TeamResponse:
    return TeamResponse.model_validate(services.join_room(session, pin, request.team_name))


@router.post("/teams/{team_id}/students", response_model=StudentResponse, tags=["teams"])
def join_team(
    team_id: int,
    session: DbSession,
    _: TeacherPrincipal,
    student_number: Annotated[str, Query(alias="studentNumber")],
) -> StudentResponse:
    return StudentResponse.model_validate(services.join_team(session, team_id, student_number))


@router.get(
    "/teams/{team_id}/progress",
    response_model=TeamProgressResponse,
    tags=["game"],
)
def get_team_progress(
    team_id: int,
    session: DbSession,
    principal: CurrentPrincipal,
) -> TeamProgressResponse:
    if principal.role == "student":
        _require_own_team(principal, team_id)
    return TeamProgressResponse.model_validate(services.build_team_progress(session, team_id))


@router.post(
    "/teams/{team_id}/answers/batch",
    response_model=BatchAnswerSubmitResponse,
    tags=["game"],
)
def submit_answers_batch(
    team_id: int,
    request: BatchAnswerSubmitRequest,
    session: DbSession,
    principal: StudentPrincipal,
) -> BatchAnswerSubmitResponse:
    _require_own_team(principal, team_id)
    progress, graded_count = services.submit_answer_batch(session, team_id, request.answers)
    return BatchAnswerSubmitResponse.model_validate({**progress, "gradedCount": graded_count})


@router.post(
    "/teams/{team_id}/answers/{question_id}",
    response_model=AnswerResponse,
    tags=["game"],
    deprecated=True,
)
def submit_answer(
    team_id: int,
    question_id: int,
    request: AnswerSubmitRequest,
    session: DbSession,
    principal: StudentPrincipal,
) -> AnswerResponse:
    _require_own_team(principal, team_id)
    return AnswerResponse.model_validate(
        services.submit_answer(
            session,
            team_id,
            question_id,
            request.submitted_answer,
        )
    )


@router.get("/rooms/{room_id}/ranking", response_model=list[RankingResponse], tags=["rooms"])
def get_ranking(
    room_id: int,
    session: DbSession,
    principal: CurrentPrincipal,
) -> list[RankingResponse]:
    if principal.role == "student":
        team = session.get(Team, principal.team_id)
        if team is None or team.room_id != room_id:
            raise DomainError("다른 방의 순위에는 접근할 수 없습니다.", 403)
    teams = services.get_ranking(session, room_id)
    return [
        RankingResponse(
            rank=index,
            teamName=team.name,
            currentCount=team.current_count,
            finished=team.finished,
            finishedAt=team.finished_at,
        )
        for index, team in enumerate(teams, start=1)
    ]
