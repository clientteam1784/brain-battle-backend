from fastapi.testclient import TestClient


def teacher_headers(client: TestClient) -> dict[str, str]:
    response = client.post("/auth/teacher", json={"accessCode": "test-teacher-code"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['accessToken']}"}


def student_headers(
    client: TestClient,
    team_pin: str,
    student_number: str = "20260001",
) -> dict[str, str]:
    response = client.post(
        "/auth/student",
        json={"teamPin": team_pin, "studentNumber": student_number},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['accessToken']}"}


def create_question(
    client: TestClient,
    headers: dict[str, str],
    number: int,
    max_submit_count: int = 2,
) -> dict:
    response = client.post(
        "/questions",
        headers=headers,
        json={
            "questionNumber": number,
            "answer": f"정답{number}",
            "maxSubmitCount": max_submit_count,
        },
    )
    assert response.status_code == 200
    return response.json()


def create_ten_questions(client: TestClient, headers: dict[str, str]) -> list[dict]:
    return [
        create_question(
            client,
            headers,
            number,
            max_submit_count=1 if number == 4 else 2,
        )
        for number in range(1, 11)
    ]


def create_team(
    client: TestClient,
    headers: dict[str, str],
    name: str = "1모둠",
) -> tuple[dict, dict]:
    room_response = client.post("/rooms", headers=headers)
    assert room_response.status_code == 200
    room = room_response.json()
    team_response = client.post(
        f"/rooms/{room['id']}/teams",
        headers=headers,
        json={"teamName": name},
    )
    assert team_response.status_code == 200
    return room, team_response.json()


def start_room(client: TestClient, headers: dict[str, str], room_id: int) -> None:
    response = client.patch(f"/rooms/{room_id}/start", headers=headers)
    assert response.status_code == 200


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_role_authentication_and_authorization(client: TestClient) -> None:
    assert client.post("/rooms").status_code == 401
    assert client.post("/auth/teacher", json={"accessCode": "wrong"}).status_code == 401

    teacher = teacher_headers(client)
    create_ten_questions(client, teacher)
    _, team = create_team(client, teacher)
    student = student_headers(client, team["pin"])

    assert client.post("/rooms", headers=student).status_code == 403
    invalid_pin = client.post(
        "/auth/student",
        json={"teamPin": "000000", "studentNumber": "20260002"},
    )
    assert invalid_pin.status_code == 401


def test_question_crud_and_validation_contract(client: TestClient) -> None:
    headers = teacher_headers(client)
    question = create_question(client, headers, 2)
    assert question == {"id": 1, "questionNumber": 2, "maxSubmitCount": 2}

    invalid = client.post(
        "/questions",
        headers=headers,
        json={"questionNumber": 0, "answer": "", "maxSubmitCount": 0},
    )
    assert invalid.status_code == 400
    assert invalid.json() == {"status": 400, "message": "문제 번호는 1 이상이어야 합니다."}

    missing_answer = client.post(
        "/questions",
        headers=headers,
        json={"questionNumber": 3, "answer": " ", "maxSubmitCount": 2},
    )
    assert missing_answer.status_code == 400
    assert missing_answer.json() == {"status": 400, "message": "정답은 필수입니다."}

    invalid_limit = client.post(
        "/questions",
        headers=headers,
        json={"questionNumber": 3, "answer": "정답", "maxSubmitCount": 0},
    )
    assert invalid_limit.status_code == 400
    assert invalid_limit.json() == {
        "status": 400,
        "message": "최대 제출 횟수는 1 이상이어야 합니다.",
    }

    updated = client.patch(
        f"/questions/{question['id']}",
        headers=headers,
        json={"questionNumber": 1, "answer": "새 정답", "maxSubmitCount": 3},
    )
    assert updated.status_code == 200
    assert updated.json()["questionNumber"] == 1

    listed = client.get("/questions", headers=headers)
    assert listed.json() == [{"id": 1, "questionNumber": 1, "maxSubmitCount": 3}]
    deleted = client.delete(f"/questions/{question['id']}", headers=headers)
    assert deleted.status_code == 200
    assert deleted.json() == {}
    missing_question = client.delete(f"/questions/{question['id']}", headers=headers)
    assert missing_question.status_code == 404
    assert missing_question.json() == {"status": 404, "message": "존재하지 않는 문제입니다."}


def test_room_requires_exactly_ten_questions_to_start(client: TestClient) -> None:
    headers = teacher_headers(client)
    create_question(client, headers, 1)
    room, _ = create_team(client, headers)

    response = client.patch(f"/rooms/{room['id']}/start", headers=headers)
    assert response.status_code == 400
    assert response.json() == {"message": "게임 시작 전 1번부터 10번까지 문제를 등록해야 합니다."}


def test_team_pin_login_and_duplicate_team(client: TestClient) -> None:
    headers = teacher_headers(client)
    room, team = create_team(client, headers, "파이썬팀")
    assert len(room["pin"]) == 6
    assert len(team["pin"]) == 6
    assert team["submissionRound"] == 0

    duplicate = client.post(
        f"/rooms/{room['id']}/teams",
        headers=headers,
        json={"teamName": "파이썬팀"},
    )
    assert duplicate.status_code == 400

    token = client.post(
        "/auth/student",
        json={"teamPin": team["pin"], "studentNumber": "20260001"},
    )
    assert token.status_code == 200
    assert token.json()["role"] == "student"
    assert token.json()["teamId"] == team["id"]
    assert token.json()["studentId"] == 1


def test_specified_summary_endpoints_and_errors(client: TestClient) -> None:
    teacher = teacher_headers(client)
    questions = create_ten_questions(client, teacher)
    room, team = create_team(client, teacher)
    other_room, other_team = create_team(client, teacher, "다른 방 모둠")

    teams = client.get(f"/rooms/{room['id']}/teams", headers=teacher)
    assert teams.status_code == 200
    assert teams.json() == [
        {"id": team["id"], "name": team["name"], "currentCount": 0, "finished": False}
    ]
    missing_room = client.get("/rooms/999/teams", headers=teacher)
    assert missing_room.status_code == 404
    assert missing_room.json() == {"status": 404, "message": "존재하지 않는 방입니다."}
    missing_start = client.patch("/rooms/999/start", headers=teacher)
    assert missing_start.status_code == 404
    assert missing_start.json() == {"status": 404, "message": "존재하지 않는 방입니다."}

    start_room(client, teacher, room["id"])
    started_again = client.patch(f"/rooms/{room['id']}/start", headers=teacher)
    assert started_again.status_code == 400
    assert started_again.json() == {"status": 400, "message": "이미 시작된 게임입니다."}

    student = student_headers(client, team["pin"])
    assert client.get(f"/teams/{team['id']}/score", headers=student).json() == {"currentCount": 0}
    assert client.get(f"/teams/{team['id']}/remaining", headers=student).json() == {
        "remainingCount": 10
    }
    assert (
        client.get(f"/teams/{team['id']}/answers/{questions[0]['id']}", headers=student).status_code
        == 404
    )

    submitted = client.post(
        f"/teams/{team['id']}/answers/{questions[0]['id']}",
        headers=student,
        json={"submittedAnswer": "틀림"},
    )
    assert submitted.status_code == 200
    assert client.get(
        f"/teams/{team['id']}/answers/{questions[0]['id']}", headers=student
    ).json() == {
        "submitCount": 1,
        "modifyCount": 0,
    }
    corrected = client.post(
        f"/teams/{team['id']}/answers/{questions[0]['id']}",
        headers=student,
        json={"submittedAnswer": "정답1"},
    )
    assert corrected.status_code == 200
    assert client.get(
        f"/teams/{team['id']}/answers/{questions[0]['id']}", headers=student
    ).json() == {
        "submitCount": 2,
        "modifyCount": 1,
    }
    assert client.get(f"/teams/{team['id']}/score", headers=student).json() == {"currentCount": 1}
    assert client.get(f"/teams/{team['id']}/remaining", headers=student).json() == {
        "remainingCount": 9
    }
    assert client.get(f"/teams/{other_team['id']}/score", headers=student).status_code == 403
    assert client.get(f"/rooms/{other_room['id']}/ranking", headers=student).status_code == 403


def test_batch_grading_distinguishes_unsubmitted_wrong_and_exhausted(
    client: TestClient,
) -> None:
    teacher = teacher_headers(client)
    questions = create_ten_questions(client, teacher)
    room, team = create_team(client, teacher)
    start_room(client, teacher, room["id"])
    student = student_headers(client, team["pin"])

    answers = [
        {"questionId": questions[0]["id"], "submittedAnswer": "정답1"},
        {"questionId": questions[1]["id"], "submittedAnswer": "오답"},
        {"questionId": questions[2]["id"], "submittedAnswer": None},
        {"questionId": questions[3]["id"], "submittedAnswer": "오답"},
    ]
    answers.extend(
        {
            "questionId": question["id"],
            "submittedAnswer": f"정답{question['questionNumber']}",
        }
        for question in questions[4:]
    )
    response = client.post(
        f"/teams/{team['id']}/answers/batch",
        headers=student,
        json={"answers": answers},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["submissionRound"] == 1
    assert payload["gradedCount"] == 9
    assert payload["correctCount"] == 7
    assert payload["rotationQuestionIds"] == [questions[1]["id"], questions[2]["id"]]
    assert payload["nextQuestionId"] == questions[1]["id"]

    progress = {item["questionNumber"]: item for item in payload["questions"]}
    assert progress[1]["status"] == "CORRECT"
    assert progress[1]["locked"] is True
    assert progress[2]["status"] == "WRONG"
    assert progress[2]["wrongCount"] == 1
    assert progress[2]["remainingAttempts"] == 1
    assert progress[3]["status"] == "UNSUBMITTED"
    assert progress[3]["wrongCount"] == 0
    assert progress[4]["status"] == "EXHAUSTED"
    assert progress[4]["locked"] is True

    second = client.post(
        f"/teams/{team['id']}/answers/batch",
        headers=student,
        json={
            "answers": [
                {"questionId": questions[1]["id"], "submittedAnswer": "정답2"},
                {"questionId": questions[2]["id"], "submittedAnswer": ""},
            ]
        },
    )
    assert second.status_code == 200
    second_payload = second.json()
    assert second_payload["gradedCount"] == 1
    assert second_payload["rotationQuestionIds"] == [questions[2]["id"]]
    question_three = next(
        item for item in second_payload["questions"] if item["questionNumber"] == 3
    )
    assert question_three["status"] == "UNSUBMITTED"
    assert question_three["wrongCount"] == 0


def test_student_scope_and_all_correct_completion(client: TestClient) -> None:
    teacher = teacher_headers(client)
    questions = create_ten_questions(client, teacher)
    room, team = create_team(client, teacher, "A팀")
    other_team = client.post(
        f"/rooms/{room['id']}/teams",
        headers=teacher,
        json={"teamName": "B팀"},
    ).json()
    start_room(client, teacher, room["id"])
    student = student_headers(client, team["pin"])

    assert client.get(f"/teams/{other_team['id']}/progress", headers=student).status_code == 403
    response = client.post(
        f"/teams/{team['id']}/answers/batch",
        headers=student,
        json={
            "answers": [
                {
                    "questionId": question["id"],
                    "submittedAnswer": f"정답{question['questionNumber']}",
                }
                for question in questions
            ]
        },
    )
    assert response.status_code == 200
    assert response.json()["finished"] is True
    assert response.json()["correctCount"] == 10
    assert response.json()["rotationQuestionIds"] == []

    ranking = client.get(f"/rooms/{room['id']}/ranking", headers=student)
    assert ranking.status_code == 200
    assert ranking.json()[0]["currentCount"] == 10
    assert ranking.json()[0]["finished"] is True


def test_answer_is_rejected_before_room_starts(client: TestClient) -> None:
    teacher = teacher_headers(client)
    questions = create_ten_questions(client, teacher)
    _, team = create_team(client, teacher, "대기팀")
    student = student_headers(client, team["pin"])

    response = client.post(
        f"/teams/{team['id']}/answers/batch",
        headers=student,
        json={"answers": [{"questionId": questions[0]["id"], "submittedAnswer": "정답1"}]},
    )
    assert response.status_code == 400
    assert response.json() == {"message": "아직 게임이 시작되지 않았습니다."}
