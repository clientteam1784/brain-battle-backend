from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import InvalidTokenError

from app.config import get_settings
from app.exceptions import DomainError

Role = Literal["teacher", "student"]


@dataclass(frozen=True)
class Principal:
    role: Role
    student_id: int | None = None
    team_id: int | None = None


bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(principal: Principal) -> tuple[str, int]:
    settings = get_settings()
    expires_in = settings.jwt_expire_minutes * 60
    now = datetime.now(UTC)
    payload = {
        "sub": str(principal.student_id or "teacher"),
        "role": principal.role,
        "student_id": principal.student_id,
        "team_id": principal.team_id,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
        "iss": "brain-battle-api",
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256"), expires_in


def get_current_principal(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> Principal:
    if credentials is None:
        raise DomainError("인증이 필요합니다.", 401)
    try:
        payload = jwt.decode(
            credentials.credentials,
            get_settings().jwt_secret,
            algorithms=["HS256"],
            issuer="brain-battle-api",
        )
        role = payload.get("role")
        if role not in {"teacher", "student"}:
            raise DomainError("유효하지 않은 사용자 역할입니다.", 401)
        return Principal(
            role=role,
            student_id=payload.get("student_id"),
            team_id=payload.get("team_id"),
        )
    except InvalidTokenError as exc:
        raise DomainError("유효하지 않거나 만료된 인증 토큰입니다.", 401) from exc


CurrentPrincipal = Annotated[Principal, Depends(get_current_principal)]


def require_teacher(principal: CurrentPrincipal) -> Principal:
    if principal.role != "teacher":
        raise DomainError("선생님 권한이 필요합니다.", 403)
    return principal


def require_student(principal: CurrentPrincipal) -> Principal:
    if principal.role != "student":
        raise DomainError("학생 권한이 필요합니다.", 403)
    return principal


TeacherPrincipal = Annotated[Principal, Depends(require_teacher)]
StudentPrincipal = Annotated[Principal, Depends(require_student)]
