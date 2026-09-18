from fastapi.testclient import TestClient


def create_question(client: TestClient, number: int, answer: str = "정답") -> dict:
    response = client.post(
        "/questions",
        json={
            "questionNumber": number,
            "answer": answer,
            "maxSubmitCount": 2,
        },
    )
    assert response.status_code == 200
    return response.json()


def create_started_team(client: TestClient, name: str = "1모둠") -> tuple[int, int]:
    room_response = client.post("/rooms")
    assert room_response.status_code == 200
    room = room_response.json()
    team_response = client.post(
        f"/rooms/{room['pin']}/teams",
        json={"teamName": name},
    )
    assert team_response.status_code == 200
    team = team_response.json()
    start_response = client.patch(f"/rooms/{room['id']}/start")
    assert start_response.status_code == 200
    return room["id"], team["id"]


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_question_crud_and_validation_contract(client: TestClient) -> None:
    question = create_question(client, 2)
    assert question == {"id": 1, "questionNumber": 2, "maxSubmitCount": 2}

    invalid = client.post(
        "/questions",
        json={"questionNumber": 0, "answer": "", "maxSubmitCount": 0},
    )
    assert invalid.status_code == 400
    assert invalid.json() == {"message": "문제 번호는 1 이상이어야 합니다."}

    updated = client.patch(
        f"/questions/{question['id']}",
        json={"questionNumber": 1, "answer": "새 정답", "maxSubmitCount": 3},
    )
    assert updated.status_code == 200
    assert updated.json()["questionNumber"] == 1

    listed = client.get("/questions")
    assert listed.status_code == 200
    assert listed.json() == [{"id": 1, "questionNumber": 1, "maxSubmitCount": 3}]

    deleted = client.delete(f"/questions/{question['id']}")
    assert deleted.status_code == 204


def test_room_team_and_student_flow(client: TestClient) -> None:
    room = client.post("/rooms").json()
    assert len(room["pin"]) == 6
    assert room["started"] is False

    team = client.post(
        f"/rooms/{room['pin']}/teams",
        json={"teamName": "파이썬팀"},
    ).json()
    assert team["currentCount"] == 0

    duplicate = client.post(
        f"/rooms/{room['pin']}/teams",
        json={"teamName": "파이썬팀"},
    )
    assert duplicate.status_code == 400
    assert duplicate.json() == {"message": "이미 존재하는 모둠 이름입니다."}

    student = client.post(
        f"/teams/{team['id']}/students",
        params={"studentNumber": "20260001"},
    )
    assert student.status_code == 200
    assert student.json() == {
        "id": 1,
        "studentNumber": "20260001",
        "teamId": team["id"],
    }


def test_answer_submission_and_ranking(client: TestClient) -> None:
    question = create_question(client, 1, "Python")
    room_id, team_id = create_started_team(client)

    wrong = client.post(
        f"/teams/{team_id}/answers/{question['id']}",
        json={"submittedAnswer": "Java"},
    )
    assert wrong.status_code == 200
    assert wrong.json()["correct"] is False
    assert wrong.json()["submitCount"] == 1

    correct = client.post(
        f"/teams/{team_id}/answers/{question['id']}",
        json={"submittedAnswer": " python "},
    )
    assert correct.status_code == 200
    assert correct.json()["correct"] is True
    assert correct.json()["submitCount"] == 2
    assert correct.json()["modifyCount"] == 1

    ranking = client.get(f"/rooms/{room_id}/ranking")
    assert ranking.status_code == 200
    assert ranking.json()[0]["rank"] == 1
    assert ranking.json()[0]["currentCount"] == 1
    assert ranking.json()[0]["finished"] is True
    assert ranking.json()[0]["finishedAt"] is not None

    repeated = client.post(
        f"/teams/{team_id}/answers/{question['id']}",
        json={"submittedAnswer": "Python"},
    )
    assert repeated.status_code == 400
    assert repeated.json() == {"message": "이미 모든 문제를 완료한 모둠입니다."}


def test_answer_is_rejected_before_room_starts(client: TestClient) -> None:
    question = create_question(client, 1)
    room = client.post("/rooms").json()
    team = client.post(
        f"/rooms/{room['pin']}/teams",
        json={"teamName": "대기팀"},
    ).json()

    response = client.post(
        f"/teams/{team['id']}/answers/{question['id']}",
        json={"submittedAnswer": "정답"},
    )
    assert response.status_code == 400
    assert response.json() == {"message": "아직 게임이 시작되지 않았습니다."}
