# Brain Battle Frontend API Guide

이 문서는 `migration/python-fastapi` 브랜치의 Python 백엔드와 프론트엔드를 연동하기 위한 계약입니다.

## Connection

| Environment | API base URL |
| --- | --- |
| Local | `http://localhost:8000` |
| Swagger UI | `http://localhost:8000/docs` |
| OpenAPI JSON | `http://localhost:8000/openapi.json` |
| Production | 배포 주소 확정 후 프론트엔드 환경변수에 설정 |

프론트엔드에서는 API 주소를 코드에 직접 넣지 말고 환경변수로 관리합니다.

```env
VITE_API_BASE_URL=http://localhost:8000
```

Next.js를 사용한다면 공개 환경변수 이름을 `NEXT_PUBLIC_API_BASE_URL`로 변경합니다.

- 모든 JSON 요청은 `Content-Type: application/json`을 사용합니다.
- 현재 API prefix는 없습니다. 예: `/api/questions`가 아니라 `/questions`입니다.
- 현재 인증과 사용자 로그인은 없습니다. `Authorization` 헤더도 사용하지 않습니다.
- 기본 허용 origin은 `http://localhost:3000`이며 백엔드의 `CORS_ORIGINS`로 변경할 수 있습니다.

## Common error response

비즈니스 오류와 입력값 검증 오류는 다음 형식입니다.

```json
{
  "message": "존재하지 않는 모둠입니다."
}
```

| Status | Meaning |
| --- | --- |
| `400` | 입력값 또는 현재 게임 상태가 올바르지 않음 |
| `409` | 동일 답안이 동시에 제출됨 |
| `503` | 고유한 방 PIN 생성 실패 |

프론트엔드는 오류 응답의 `message`를 사용자 메시지로 표시할 수 있습니다.

## API summary

| Method | Path | Description | Success |
| --- | --- | --- | --- |
| `GET` | `/health` | 서버 상태 확인 | `200` |
| `POST` | `/questions` | 문제 생성 | `200` |
| `GET` | `/questions` | 문제 번호순 전체 조회 | `200` |
| `PATCH` | `/questions/{questionId}` | 문제 수정 | `200` |
| `DELETE` | `/questions/{questionId}` | 문제 삭제 | `204` |
| `POST` | `/rooms` | 방 생성 | `200` |
| `PATCH` | `/rooms/{roomId}/start` | 게임 시작 | `200` |
| `POST` | `/rooms/{pin}/teams` | PIN으로 팀 참가 | `200` |
| `POST` | `/teams/{teamId}/students?studentNumber=...` | 학생 등록 | `200` |
| `POST` | `/teams/{teamId}/answers/{questionId}` | 답안 제출 | `200` |
| `GET` | `/rooms/{roomId}/ranking` | 방 순위 조회 | `200` |

## Questions

### Create question

```http
POST /questions
Content-Type: application/json
```

```json
{
  "questionNumber": 1,
  "answer": "Python",
  "maxSubmitCount": 3
}
```

`questionNumber`와 `maxSubmitCount`는 1 이상이며 `answer`는 빈 문자열일 수 없습니다.

```json
{
  "id": 1,
  "questionNumber": 1,
  "maxSubmitCount": 3
}
```

정답인 `answer`는 생성 응답과 전체 조회 응답에 포함되지 않습니다.

### List questions

```http
GET /questions
```

```json
[
  {
    "id": 1,
    "questionNumber": 1,
    "maxSubmitCount": 3
  }
]
```

### Update question

```http
PATCH /questions/1
Content-Type: application/json
```

요청 body는 문제 생성과 같습니다. 부분 수정이 아니라 세 필드를 모두 전송해야 합니다.

### Delete question

```http
DELETE /questions/1
```

성공하면 body 없이 `204 No Content`를 반환합니다.

## Rooms and teams

### Create room

```http
POST /rooms
```

요청 body는 없습니다.

```json
{
  "id": 1,
  "pin": "482193",
  "started": false
}
```

`pin`은 항상 6자리 문자열이므로 숫자로 변환하지 않습니다. 앞자리 0은 현재 생성되지 않지만 문자열 계약을 유지해야 합니다.

### Join room as a team

```http
POST /rooms/482193/teams
Content-Type: application/json
```

```json
{
  "teamName": "파이썬팀"
}
```

```json
{
  "id": 7,
  "name": "파이썬팀",
  "currentCount": 0,
  "finished": false
}
```

같은 방에서는 팀 이름을 중복해서 사용할 수 없습니다.

### Start game

```http
PATCH /rooms/1/start
```

```json
{
  "id": 1,
  "pin": "482193",
  "started": true
}
```

## Students

```http
POST /teams/7/students?studentNumber=20260001
```

요청 body가 아니라 `studentNumber` query parameter를 사용합니다.

```json
{
  "id": 15,
  "studentNumber": "20260001",
  "teamId": 7
}
```

Java 구현은 ORM 엔티티를 직접 반환했지만 Python 구현은 순환 참조와 내부 정보 노출을 피하기 위해 위 세 필드만 반환합니다. 같은 팀에는 동일한 학번을 중복 등록할 수 없습니다.

## Answers

```http
POST /teams/7/answers/1
Content-Type: application/json
```

```json
{
  "submittedAnswer": "Python"
}
```

```json
{
  "id": 20,
  "submittedAnswer": "Python",
  "correct": true,
  "submitCount": 2,
  "modifyCount": 1
}
```

- 게임 시작 전에는 답안을 제출할 수 없습니다.
- 이미 맞힌 문제에는 다시 제출할 수 없습니다.
- 최대 제출 횟수에 도달하면 다시 제출할 수 없습니다.
- 정답 비교는 앞뒤 공백과 영문 대소문자를 무시합니다.
- 모든 문제를 맞히면 해당 팀의 `finished`가 `true`가 됩니다.
- 제출 버튼은 요청 처리 중 비활성화하여 동일 요청의 연속 전송을 방지해야 합니다.

## Ranking

```http
GET /rooms/1/ranking
```

```json
[
  {
    "rank": 1,
    "teamName": "파이썬팀",
    "currentCount": 10,
    "finished": true,
    "finishedAt": "2026-09-18T14:30:12.123456"
  },
  {
    "rank": 2,
    "teamName": "알고리즘팀",
    "currentCount": 8,
    "finished": false,
    "finishedAt": null
  }
]
```

정렬 기준은 다음 순서입니다.

1. 모든 문제를 완료한 팀 우선
2. 완료 팀은 완료 시간이 빠른 순서
3. 미완료 팀은 정답 수가 많은 순서
4. 나머지가 같으면 팀 ID가 빠른 순서

`finishedAt`은 timezone 정보가 없는 ISO 8601 문자열 또는 `null`입니다.

현재 WebSocket은 구현되어 있지 않습니다. 실시간 순위 화면은 우선 `GET /rooms/{roomId}/ranking`을 폴링해야 하며 권장 주기는 2초 이상입니다. 브라우저 탭이 백그라운드에 있으면 폴링을 중지하는 것이 좋습니다.

## Frontend integration checklist

- [ ] API base URL을 환경변수로 분리
- [ ] `studentNumber`를 query parameter로 전송
- [ ] 방 PIN을 문자열로 보관
- [ ] `204` 응답에서 JSON 파싱하지 않기
- [ ] `finishedAt: null` 처리
- [ ] 오류 응답의 `message` 표시
- [ ] 답안 제출 중 버튼 비활성화
- [ ] 순위 조회 폴링 시작·종료 처리
- [ ] 운영 프론트엔드 주소를 백엔드 `CORS_ORIGINS`에 등록

기계 판독 가능한 전체 계약은 같은 디렉터리의 `openapi.json`을 사용합니다.

