# 이 Python 모듈을 가져옵니다.
import secrets
# 필요한 기능/타입을 다른 모듈에서 가져옵니다.
from typing import Annotated

# 필요한 기능/타입을 다른 모듈에서 가져옵니다.
from fastapi import APIRouter, Depends, Query
# 필요한 기능/타입을 다른 모듈에서 가져옵니다.
from sqlalchemy.orm import Session

# 필요한 기능/타입을 다른 모듈에서 가져옵니다.
from app import services
# 필요한 기능/타입을 다른 모듈에서 가져옵니다.
from app.auth import (
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    CurrentPrincipal,
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    Principal,
    # 응답 스키마 객체를 만들거나 검증합니다.
    StudentPrincipal,
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    TeacherPrincipal,
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    create_access_token,
# 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
)
# 필요한 기능/타입을 다른 모듈에서 가져옵니다.
from app.config import get_settings
# 필요한 기능/타입을 다른 모듈에서 가져옵니다.
from app.database import get_session
# 필요한 기능/타입을 다른 모듈에서 가져옵니다.
from app.exceptions import DomainError
# 필요한 기능/타입을 다른 모듈에서 가져옵니다.
from app.models import Team
# 필요한 기능/타입을 다른 모듈에서 가져옵니다.
from app.schemas import (
    # 응답 스키마 객체를 만들거나 검증합니다.
    AnswerCountsResponse,
    # 응답 스키마 객체를 만들거나 검증합니다.
    AnswerSubmitRequest,
    # 응답 스키마 객체를 만들거나 검증합니다.
    AuthTokenResponse,
    # 응답 스키마 객체를 만들거나 검증합니다.
    BatchAnswerSubmitRequest,
    # 응답 스키마 객체를 만들거나 검증합니다.
    BatchAnswerSubmitResponse,
    # 응답 스키마 객체를 만들거나 검증합니다.
    QuestionRequest,
    # 응답 스키마 객체를 만들거나 검증합니다.
    QuestionResponse,
    # 응답 스키마 객체를 만들거나 검증합니다.
    RankingResponse,
    # 응답 스키마 객체를 만들거나 검증합니다.
    RemainingQuestionsResponse,
    # 응답 스키마 객체를 만들거나 검증합니다.
    RoomResponse,
    # 응답 스키마 객체를 만들거나 검증합니다.
    SingleAnswerResponse,
    # 응답 스키마 객체를 만들거나 검증합니다.
    StudentLoginRequest,
    # 응답 스키마 객체를 만들거나 검증합니다.
    StudentResponse,
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    TeacherLoginRequest,
    # 응답 스키마 객체를 만들거나 검증합니다.
    TeamJoinRequest,
    # 응답 스키마 객체를 만들거나 검증합니다.
    TeamProgressResponse,
    # 응답 스키마 객체를 만들거나 검증합니다.
    TeamResponse,
    # 응답 스키마 객체를 만들거나 검증합니다.
    TeamScoreResponse,
    # 응답 스키마 객체를 만들거나 검증합니다.
    TeamSummaryResponse,
# 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
)

# HTTP 요청을 받아 서비스 로직을 호출하고, 결과를 응답 스키마로 바꾸는 API 경계입니다.
# API 경로를 등록할 FastAPI 라우터 객체를 만듭니다.
router = APIRouter()
# DB 세션 주입 설정을 짧은 타입 별칭으로 정의합니다.
DbSession = Annotated[Session, Depends(get_session)]


# 학생 토큰에 담긴 조 ID와 요청 경로의 조 ID를 비교해 다른 조의 정보 접근을 막습니다.
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def _require_own_team(principal: Principal, team_id: int) -> None:
    # 조건을 검사하고 참이면 들여쓴 블록을 실행합니다.
    if principal.team_id != team_id:
        # 현재 요청을 중단하고 지정한 오류를 발생시킵니다.
        raise DomainError("다른 조의 정보에는 접근할 수 없습니다.", 403)


# 학생은 자신이 속한 조가 있는 방의 순위만 볼 수 있습니다.
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def _require_own_room(session: Session, principal: Principal, room_id: int) -> None:
    # 조건을 검사하고 참이면 들여쓴 블록을 실행합니다.
    if principal.role == "student":
        # 서비스 결과를 변수에 저장해 다음 단계에서 사용합니다.
        team = session.get(Team, principal.team_id)
        # 조건을 검사하고 참이면 들여쓴 블록을 실행합니다.
        if team is None or team.room_id != room_id:
            # 현재 요청을 중단하고 지정한 오류를 발생시킵니다.
            raise DomainError("다른 방의 정보에는 접근할 수 없습니다.", 403)


# 아래 함수를 HTTP 경로에 연결하고 응답 형식과 문서 태그를 지정합니다.
@router.post("/auth/teacher", response_model=AuthTokenResponse, tags=["auth"])
# 교사 인증 코드를 비교하고, 성공하면 교사용 JWT를 발급합니다.
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def login_teacher(request: TeacherLoginRequest) -> AuthTokenResponse:
    # 조건을 검사하고 참이면 들여쓴 블록을 실행합니다.
    if not secrets.compare_digest(request.access_code, get_settings().teacher_access_code):
        # 현재 요청을 중단하고 지정한 오류를 발생시킵니다.
        raise DomainError("선생님 인증 코드가 올바르지 않습니다.", 401)
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    principal = Principal(role="teacher")
    # 서비스 결과를 변수에 저장해 다음 단계에서 사용합니다.
    token, expires_in = create_access_token(principal)
    # 계산하거나 만든 값을 호출자에게 반환합니다.
    return AuthTokenResponse(
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        accessToken=token,
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        role=principal.role,
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        expiresIn=expires_in,
    # 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
    )


# 아래 함수를 HTTP 경로에 연결하고 응답 형식과 문서 태그를 지정합니다.
@router.post("/auth/student", response_model=AuthTokenResponse, tags=["auth"])
# 조 PIN과 학번으로 학생을 찾거나 등록한 뒤, 조 범위가 담긴 JWT를 발급합니다.
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def login_student(request: StudentLoginRequest, session: DbSession) -> AuthTokenResponse:
    # 서비스 결과를 변수에 저장해 다음 단계에서 사용합니다.
    student = services.authenticate_student(
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        session,
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        request.team_pin,
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        request.student_number,
    # 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
    )
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    principal = Principal(role="student", student_id=student.id, team_id=student.team_id)
    # 서비스 결과를 변수에 저장해 다음 단계에서 사용합니다.
    token, expires_in = create_access_token(principal)
    # 계산하거나 만든 값을 호출자에게 반환합니다.
    return AuthTokenResponse(
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        accessToken=token,
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        role=principal.role,
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        expiresIn=expires_in,
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        studentId=student.id,
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        teamId=student.team_id,
    # 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
    )


# 문제 관리는 교사 전용입니다. 인증 의존성이 역할을 먼저 검사합니다.
# 아래 함수를 HTTP 경로에 연결하고 응답 형식과 문서 태그를 지정합니다.
@router.post("/questions", response_model=QuestionResponse, tags=["questions"])
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def create_question(
    # 검증된 HTTP 요청 본문을 받습니다.
    request: QuestionRequest,
    # 요청에서 사용할 데이터베이스 세션을 받습니다.
    session: DbSession,
    # 값 자체는 쓰지 않지만 타입에 연결된 인증/권한 검사를 실행합니다.
    _: TeacherPrincipal,
# 함수 선언을 마치고 아래에 실행 본문을 시작합니다.
) -> QuestionResponse:
    # 서비스 결과를 변수에 저장해 다음 단계에서 사용합니다.
    question = services.create_question(
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        session,
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        request.question_number,
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        request.answer,
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        request.max_submit_count,
    # 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
    )
    # 계산하거나 만든 값을 호출자에게 반환합니다.
    return QuestionResponse.model_validate(question)


# 아래 함수를 HTTP 경로에 연결하고 응답 형식과 문서 태그를 지정합니다.
@router.get("/questions", response_model=list[QuestionResponse], tags=["questions"])
# 로그인한 사용자에게 문제 목록을 문제 번호 순서로 반환합니다.
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def get_questions(session: DbSession, _: CurrentPrincipal) -> list[QuestionResponse]:
    # 계산하거나 만든 값을 호출자에게 반환합니다.
    return [QuestionResponse.model_validate(item) for item in services.list_questions(session)]


# 아래 함수를 HTTP 경로에 연결하고 응답 형식과 문서 태그를 지정합니다.
@router.patch(
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    "/questions/{question_id}",
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    response_model=QuestionResponse,
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    tags=["questions"],
# 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
)
# 교사가 기존 문제의 번호, 정답, 제출 가능 횟수를 변경합니다.
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def update_question(
    # URL 경로에서 해당 리소스의 식별자를 받습니다.
    question_id: int,
    # 검증된 HTTP 요청 본문을 받습니다.
    request: QuestionRequest,
    # 요청에서 사용할 데이터베이스 세션을 받습니다.
    session: DbSession,
    # 값 자체는 쓰지 않지만 타입에 연결된 인증/권한 검사를 실행합니다.
    _: TeacherPrincipal,
# 함수 선언을 마치고 아래에 실행 본문을 시작합니다.
) -> QuestionResponse:
    # 서비스 결과를 변수에 저장해 다음 단계에서 사용합니다.
    question = services.update_question(
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        session,
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        question_id,
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        request.question_number,
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        request.answer,
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        request.max_submit_count,
    # 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
    )
    # 계산하거나 만든 값을 호출자에게 반환합니다.
    return QuestionResponse.model_validate(question)


# 아래 함수를 HTTP 경로에 연결하고 응답 형식과 문서 태그를 지정합니다.
@router.delete(
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    "/questions/{question_id}",
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    tags=["questions"],
# 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
)
# 교사가 문제를 삭제합니다. 연결된 답안은 DB 외래 키 정책에 따라 함께 삭제됩니다.
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def delete_question(
    # URL 경로에서 해당 리소스의 식별자를 받습니다.
    question_id: int,
    # 요청에서 사용할 데이터베이스 세션을 받습니다.
    session: DbSession,
    # 값 자체는 쓰지 않지만 타입에 연결된 인증/권한 검사를 실행합니다.
    _: TeacherPrincipal,
# 함수 선언을 마치고 아래에 실행 본문을 시작합니다.
) -> dict:
    # 실제 업무 규칙을 담당하는 서비스 함수를 호출합니다.
    services.delete_question(session, question_id)
    # 계산하거나 만든 값을 호출자에게 반환합니다.
    return {}


# 방과 조 구성은 교사가 관리하고, 게임 진행 조회와 답안 제출은 학생도 사용합니다.
# 아래 함수를 HTTP 경로에 연결하고 응답 형식과 문서 태그를 지정합니다.
@router.post("/rooms", response_model=RoomResponse, tags=["rooms"])
# 교사가 새 게임 방을 만들고 참가용 PIN을 받습니다.
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def create_room(session: DbSession, _: TeacherPrincipal) -> RoomResponse:
    # 계산하거나 만든 값을 호출자에게 반환합니다.
    return RoomResponse.model_validate(services.create_room(session))


# 아래 함수를 HTTP 경로에 연결하고 응답 형식과 문서 태그를 지정합니다.
@router.patch("/rooms/{room_id}/start", response_model=RoomResponse, tags=["rooms"])
# 등록된 문제 세트를 검증한 뒤 교사가 게임을 시작합니다.
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def start_room(
    # URL 경로에서 해당 리소스의 식별자를 받습니다.
    room_id: int,
    # 요청에서 사용할 데이터베이스 세션을 받습니다.
    session: DbSession,
    # 값 자체는 쓰지 않지만 타입에 연결된 인증/권한 검사를 실행합니다.
    _: TeacherPrincipal,
# 함수 선언을 마치고 아래에 실행 본문을 시작합니다.
) -> RoomResponse:
    # 계산하거나 만든 값을 호출자에게 반환합니다.
    return RoomResponse.model_validate(services.start_room(session, room_id))


# 아래 함수를 HTTP 경로에 연결하고 응답 형식과 문서 태그를 지정합니다.
@router.get("/rooms/{room_id}/teams", response_model=list[TeamSummaryResponse], tags=["teams"])
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def get_room_teams(
    # URL 경로에서 해당 리소스의 식별자를 받습니다.
    room_id: int,
    # 요청에서 사용할 데이터베이스 세션을 받습니다.
    session: DbSession,
    # 값 자체는 쓰지 않지만 타입에 연결된 인증/권한 검사를 실행합니다.
    _: TeacherPrincipal,
# 함수 선언을 마치고 아래에 실행 본문을 시작합니다.
) -> list[TeamSummaryResponse]:
    # 계산하거나 만든 값을 호출자에게 반환합니다.
    return [
        # 응답 스키마 객체를 만들거나 검증합니다.
        TeamSummaryResponse.model_validate(team)
        # 목록의 각 항목을 차례대로 처리합니다.
        for team in services.list_room_teams(session, room_id)
    # 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
    ]


# 아래 함수를 HTTP 경로에 연결하고 응답 형식과 문서 태그를 지정합니다.
@router.post("/rooms/{room_id}/teams", response_model=TeamResponse, tags=["teams"])
# 교사가 방 안에 새 모둠을 만들고 학생용 PIN을 발급합니다.
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def create_team(
    # URL 경로에서 해당 리소스의 식별자를 받습니다.
    room_id: int,
    # 검증된 HTTP 요청 본문을 받습니다.
    request: TeamJoinRequest,
    # 요청에서 사용할 데이터베이스 세션을 받습니다.
    session: DbSession,
    # 값 자체는 쓰지 않지만 타입에 연결된 인증/권한 검사를 실행합니다.
    _: TeacherPrincipal,
# 함수 선언을 마치고 아래에 실행 본문을 시작합니다.
) -> TeamResponse:
    # 계산하거나 만든 값을 호출자에게 반환합니다.
    return TeamResponse.model_validate(services.create_team(session, room_id, request.team_name))


# 아래 함수를 HTTP 경로에 연결하고 응답 형식과 문서 태그를 지정합니다.
@router.post("/teams/{team_id}/students", response_model=StudentResponse, tags=["teams"])
# 교사가 지정한 모둠에 학번을 등록합니다.
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def join_team(
    # URL 경로에서 해당 리소스의 식별자를 받습니다.
    team_id: int,
    # 요청에서 사용할 데이터베이스 세션을 받습니다.
    session: DbSession,
    # 값 자체는 쓰지 않지만 타입에 연결된 인증/권한 검사를 실행합니다.
    _: TeacherPrincipal,
    # 쿼리 문자열에서 학번을 읽고 외부 이름을 studentNumber로 지정합니다.
    student_number: Annotated[str, Query(alias="studentNumber")],
# 함수 선언을 마치고 아래에 실행 본문을 시작합니다.
) -> StudentResponse:
    # 계산하거나 만든 값을 호출자에게 반환합니다.
    return StudentResponse.model_validate(services.join_team(session, team_id, student_number))


# 아래 함수를 HTTP 경로에 연결하고 응답 형식과 문서 태그를 지정합니다.
@router.get(
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    "/teams/{team_id}/progress",
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    response_model=TeamProgressResponse,
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    tags=["game"],
# 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
)
# 문항별 정답 여부와 다음 제출 대상 등 게임 진행 정보를 반환합니다.
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def get_team_progress(
    # URL 경로에서 해당 리소스의 식별자를 받습니다.
    team_id: int,
    # 요청에서 사용할 데이터베이스 세션을 받습니다.
    session: DbSession,
    # 인증된 사용자의 역할과 식별 정보를 받습니다.
    principal: CurrentPrincipal,
# 함수 선언을 마치고 아래에 실행 본문을 시작합니다.
) -> TeamProgressResponse:
    # 조건을 검사하고 참이면 들여쓴 블록을 실행합니다.
    if principal.role == "student":
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        _require_own_team(principal, team_id)
    # 계산하거나 만든 값을 호출자에게 반환합니다.
    return TeamProgressResponse.model_validate(services.build_team_progress(session, team_id))


# 아래 함수를 HTTP 경로에 연결하고 응답 형식과 문서 태그를 지정합니다.
@router.get("/teams/{team_id}/score", response_model=TeamScoreResponse, tags=["game"])
# 해당 모둠의 현재 정답 개수를 반환합니다.
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def get_team_score(
    # URL 경로에서 해당 리소스의 식별자를 받습니다.
    team_id: int,
    # 요청에서 사용할 데이터베이스 세션을 받습니다.
    session: DbSession,
    # 인증된 사용자의 역할과 식별 정보를 받습니다.
    principal: CurrentPrincipal,
# 함수 선언을 마치고 아래에 실행 본문을 시작합니다.
) -> TeamScoreResponse:
    # 조건을 검사하고 참이면 들여쓴 블록을 실행합니다.
    if principal.role == "student":
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        _require_own_team(principal, team_id)
    # 서비스 결과를 변수에 저장해 다음 단계에서 사용합니다.
    team = services.get_team(session, team_id)
    # 계산하거나 만든 값을 호출자에게 반환합니다.
    return TeamScoreResponse(currentCount=team.current_count)


# 아래 함수를 HTTP 경로에 연결하고 응답 형식과 문서 태그를 지정합니다.
@router.get(
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    "/teams/{team_id}/remaining",
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    response_model=RemainingQuestionsResponse,
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    tags=["game"],
# 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
)
# 전체 문제 수에서 정답 처리된 수를 빼 남은 문제 수를 계산합니다.
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def get_remaining_questions(
    # URL 경로에서 해당 리소스의 식별자를 받습니다.
    team_id: int,
    # 요청에서 사용할 데이터베이스 세션을 받습니다.
    session: DbSession,
    # 인증된 사용자의 역할과 식별 정보를 받습니다.
    principal: CurrentPrincipal,
# 함수 선언을 마치고 아래에 실행 본문을 시작합니다.
) -> RemainingQuestionsResponse:
    # 조건을 검사하고 참이면 들여쓴 블록을 실행합니다.
    if principal.role == "student":
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        _require_own_team(principal, team_id)
    # 서비스 결과를 변수에 저장해 다음 단계에서 사용합니다.
    team = services.get_team(session, team_id)
    # 계산하거나 만든 값을 호출자에게 반환합니다.
    return RemainingQuestionsResponse(
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        remainingCount=max(len(services.list_questions(session)) - team.current_count, 0)
    # 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
    )


# 아래 함수를 HTTP 경로에 연결하고 응답 형식과 문서 태그를 지정합니다.
@router.get(
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    "/teams/{team_id}/answers/{question_id}",
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    response_model=AnswerCountsResponse,
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    tags=["game"],
# 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
)
# 특정 모둠과 문제 조합의 제출 및 수정 횟수를 조회합니다.
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def get_answer_counts(
    # URL 경로에서 해당 리소스의 식별자를 받습니다.
    team_id: int,
    # URL 경로에서 해당 리소스의 식별자를 받습니다.
    question_id: int,
    # 요청에서 사용할 데이터베이스 세션을 받습니다.
    session: DbSession,
    # 인증된 사용자의 역할과 식별 정보를 받습니다.
    principal: CurrentPrincipal,
# 함수 선언을 마치고 아래에 실행 본문을 시작합니다.
) -> AnswerCountsResponse:
    # 조건을 검사하고 참이면 들여쓴 블록을 실행합니다.
    if principal.role == "student":
        # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
        _require_own_team(principal, team_id)
    # 계산하거나 만든 값을 호출자에게 반환합니다.
    return AnswerCountsResponse.model_validate(services.get_answer(session, team_id, question_id))


# 현재 프론트엔드의 기본 제출 경로입니다. 한 번의 요청에서 여러 문항을 채점합니다.
# 아래 함수를 HTTP 경로에 연결하고 응답 형식과 문서 태그를 지정합니다.
@router.post(
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    "/teams/{team_id}/answers/batch",
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    response_model=BatchAnswerSubmitResponse,
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    tags=["game"],
# 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
)
# 학생이 제출한 답안 묶음을 채점하고 최신 진행 상황을 반환합니다.
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def submit_answers_batch(
    # URL 경로에서 해당 리소스의 식별자를 받습니다.
    team_id: int,
    # 검증된 HTTP 요청 본문을 받습니다.
    request: BatchAnswerSubmitRequest,
    # 요청에서 사용할 데이터베이스 세션을 받습니다.
    session: DbSession,
    # 인증된 사용자의 역할과 식별 정보를 받습니다.
    principal: StudentPrincipal,
# 함수 선언을 마치고 아래에 실행 본문을 시작합니다.
) -> BatchAnswerSubmitResponse:
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    _require_own_team(principal, team_id)
    # 서비스 결과를 변수에 저장해 다음 단계에서 사용합니다.
    progress, graded_count = services.submit_answer_batch(session, team_id, request.answers)
    # 계산하거나 만든 값을 호출자에게 반환합니다.
    return BatchAnswerSubmitResponse.model_validate({**progress, "gradedCount": graded_count})


# 이전 단일 답안 API와의 호환을 위해 남겨 둔 경로입니다.
# 아래 함수를 HTTP 경로에 연결하고 응답 형식과 문서 태그를 지정합니다.
@router.post(
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    "/teams/{team_id}/answers/{question_id}",
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    response_model=SingleAnswerResponse,
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    tags=["game"],
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    deprecated=True,
# 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
)
# 이전 버전 클라이언트용 단일 문항 제출 API입니다.
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def submit_answer(
    # URL 경로에서 해당 리소스의 식별자를 받습니다.
    team_id: int,
    # URL 경로에서 해당 리소스의 식별자를 받습니다.
    question_id: int,
    # 검증된 HTTP 요청 본문을 받습니다.
    request: AnswerSubmitRequest,
    # 요청에서 사용할 데이터베이스 세션을 받습니다.
    session: DbSession,
    # 인증된 사용자의 역할과 식별 정보를 받습니다.
    principal: StudentPrincipal,
# 함수 선언을 마치고 아래에 실행 본문을 시작합니다.
) -> SingleAnswerResponse:
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    _require_own_team(principal, team_id)
    # 계산하거나 만든 값을 호출자에게 반환합니다.
    return SingleAnswerResponse.model_validate(
        # 실제 업무 규칙을 담당하는 서비스 함수를 호출합니다.
        services.submit_answer(
            # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
            session,
            # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
            team_id,
            # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
            question_id,
            # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
            request.submitted_answer,
        # 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
        )
    # 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
    )


# 아래 함수를 HTTP 경로에 연결하고 응답 형식과 문서 태그를 지정합니다.
@router.get("/rooms/{room_id}/ranking", response_model=list[RankingResponse], tags=["rooms"])
# 방의 모둠을 순위로 바꾸고 순번을 붙여 반환합니다.
# 요청 처리 함수의 이름과 입력/반환 타입을 선언합니다.
def get_ranking(
    # URL 경로에서 해당 리소스의 식별자를 받습니다.
    room_id: int,
    # 요청에서 사용할 데이터베이스 세션을 받습니다.
    session: DbSession,
    # 인증된 사용자의 역할과 식별 정보를 받습니다.
    principal: CurrentPrincipal,
# 함수 선언을 마치고 아래에 실행 본문을 시작합니다.
) -> list[RankingResponse]:
    # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
    _require_own_room(session, principal, room_id)
    # 서비스 결과를 변수에 저장해 다음 단계에서 사용합니다.
    teams = services.get_ranking(session, room_id)
    # 계산하거나 만든 값을 호출자에게 반환합니다.
    return [
        # 응답 스키마 객체를 만들거나 검증합니다.
        RankingResponse(
            # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
            rank=index,
            # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
            teamName=team.name,
            # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
            currentCount=team.current_count,
            # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
            finished=team.finished,
            # 이 줄은 API 입력을 검사하거나 서비스 결과를 응답 데이터로 구성합니다.
            finishedAt=team.finished_at,
        # 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
        )
        # 목록의 각 항목을 차례대로 처리합니다.
        for index, team in enumerate(teams, start=1)
    # 여러 줄로 작성한 호출/목록의 괄호를 닫습니다.
    ]
