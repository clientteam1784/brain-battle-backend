from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app import services
from app.database import get_session
from app.schemas import (
    AnswerResponse,
    AnswerSubmitRequest,
    QuestionRequest,
    QuestionResponse,
    RankingResponse,
    RoomResponse,
    StudentResponse,
    TeamJoinRequest,
    TeamResponse,
)

router = APIRouter()
DbSession = Annotated[Session, Depends(get_session)]


@router.post("/questions", response_model=QuestionResponse)
def create_question(request: QuestionRequest, session: DbSession) -> QuestionResponse:
    question = services.create_question(
        session,
        request.question_number,
        request.answer,
        request.max_submit_count,
    )
    return QuestionResponse.model_validate(question)


@router.get("/questions", response_model=list[QuestionResponse])
def get_questions(session: DbSession) -> list[QuestionResponse]:
    return [QuestionResponse.model_validate(item) for item in services.list_questions(session)]


@router.patch("/questions/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int,
    request: QuestionRequest,
    session: DbSession,
) -> QuestionResponse:
    question = services.update_question(
        session,
        question_id,
        request.question_number,
        request.answer,
        request.max_submit_count,
    )
    return QuestionResponse.model_validate(question)


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(question_id: int, session: DbSession) -> Response:
    services.delete_question(session, question_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/rooms", response_model=RoomResponse)
def create_room(session: DbSession) -> RoomResponse:
    return RoomResponse.model_validate(services.create_room(session))


@router.patch("/rooms/{room_id}/start", response_model=RoomResponse)
def start_room(room_id: int, session: DbSession) -> RoomResponse:
    return RoomResponse.model_validate(services.start_room(session, room_id))


@router.post("/rooms/{pin}/teams", response_model=TeamResponse)
def join_room(
    pin: str,
    request: TeamJoinRequest,
    session: DbSession,
) -> TeamResponse:
    return TeamResponse.model_validate(services.join_room(session, pin, request.team_name))


@router.post("/teams/{team_id}/students", response_model=StudentResponse)
def join_team(
    team_id: int,
    session: DbSession,
    student_number: Annotated[str, Query(alias="studentNumber")],
) -> StudentResponse:
    return StudentResponse.model_validate(services.join_team(session, team_id, student_number))


@router.post(
    "/teams/{team_id}/answers/{question_id}",
    response_model=AnswerResponse,
)
def submit_answer(
    team_id: int,
    question_id: int,
    request: AnswerSubmitRequest,
    session: DbSession,
) -> AnswerResponse:
    return AnswerResponse.model_validate(
        services.submit_answer(
            session,
            team_id,
            question_id,
            request.submitted_answer,
        )
    )


@router.get("/rooms/{room_id}/ranking", response_model=list[RankingResponse])
def get_ranking(room_id: int, session: DbSession) -> list[RankingResponse]:
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
