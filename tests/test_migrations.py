import os
import subprocess
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import get_session
from app.main import app

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def migrated_client(tmp_path: Path) -> TestClient:
    """Alembic으로 만든 SQLite DB를 쓰는 클라이언트입니다(create_all로는 못 잡는 차이 검증)."""
    db_url = f"sqlite:///{(tmp_path / 'migrated.db').as_posix()}"
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=ROOT,
        env={**os.environ, "DATABASE_URL": db_url},
        check=True,
        capture_output=True,
    )
    engine = create_engine(db_url)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_session():
        with factory() as session:  # type: Session
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    engine.dispose()


def _teacher_headers(client: TestClient) -> dict[str, str]:
    response = client.post("/auth/teacher", json={"accessCode": "test-teacher-code"})
    return {"Authorization": f"Bearer {response.json()['accessToken']}"}


def test_migrated_schema_autogenerates_ids(migrated_client: TestClient) -> None:
    headers = _teacher_headers(migrated_client)

    question = migrated_client.post(
        "/questions",
        headers=headers,
        json={"questionNumber": 1, "answer": "a", "maxSubmitCount": 3},
    )
    assert question.status_code == 200
    assert question.json()["id"] == 1

    room = migrated_client.post("/rooms", headers=headers)
    assert room.status_code == 200

    team = migrated_client.post(
        f"/rooms/{room.json()['id']}/teams", headers=headers, json={"teamName": "A"}
    )
    assert team.status_code == 200


def test_duplicate_question_number_is_still_reported(migrated_client: TestClient) -> None:
    headers = _teacher_headers(migrated_client)
    body = {"questionNumber": 1, "answer": "a", "maxSubmitCount": 3}
    assert migrated_client.post("/questions", headers=headers, json=body).status_code == 200

    duplicate = migrated_client.post("/questions", headers=headers, json=body)
    assert duplicate.status_code == 400
    assert duplicate.json()["message"] == "이미 존재하는 문제 번호입니다."
