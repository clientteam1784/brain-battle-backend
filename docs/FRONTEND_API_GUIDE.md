# Brain Battle 프론트엔드 API 가이드

모든 API의 요청·응답·오류를 확인하려면 [전체 API 명세서](./API_SPEC.md)를 참고합니다.
이 문서는 프론트 화면을 연결하는 순서와 제출 흐름을 설명합니다.

현재 `main` 브랜치의 Python/FastAPI 백엔드 계약입니다. 로컬 API 주소는
`http://localhost:8000`이고 Swagger UI는 `/docs`에서 볼 수 있습니다.

## 공통 규칙

- `/health`와 로그인 API 이외의 모든 API는 `Authorization: Bearer {accessToken}` 헤더가 필요합니다.
- 교사 전용 API를 학생 토큰으로 호출하면 `403`, 토큰이 없거나 유효하지 않으면 `401`입니다.
- PIN과 학번은 앞자리 0 보존을 위해 항상 문자열로 처리합니다.
- 오류 응답은 보통 `{"message": "오류 내용"}` 형식입니다. 문제 관리, 게임 시작,
  모둠 목록 조회의 일부 오류는 제공된 명세대로 `status` 숫자도 포함합니다.
- 기본 CORS origin은 `http://localhost:3000`이며 서버의 `CORS_ORIGINS`로 변경합니다.

## 로그인과 역할

### 교사 로그인

```http
POST /auth/teacher
Content-Type: application/json

{"accessCode": "교사용 접근 코드"}
```

### 학생 로그인

교사가 팀 생성 시 받은 `pin`을 학생에게 전달합니다. 이 PIN을 아는 학생만 해당 팀으로
로그인할 수 있습니다. 처음 로그인한 학번은 해당 팀에 자동 등록됩니다.

```http
POST /auth/student
Content-Type: application/json

{"teamPin": "583021", "studentNumber": "20260001"}
```

두 로그인 응답의 공통 형식입니다.

```json
{
  "accessToken": "eyJ...",
  "tokenType": "bearer",
  "role": "student",
  "expiresIn": 28800,
  "studentId": 15,
  "teamId": 7
}
```

교사 로그인에서는 `studentId`와 `teamId`가 `null`입니다. 토큰은 기본 8시간 유효하며,
프론트엔드는 `401`을 받으면 로그인 화면으로 이동합니다.

## API 권한 요약

| Method | Path | 권한 | 설명 |
| --- | --- | --- | --- |
| `POST` | `/auth/teacher` | 공개 | 교사 로그인 |
| `POST` | `/auth/student` | 공개 | 팀 PIN으로 학생 로그인 |
| `POST/PATCH/DELETE` | `/questions...` | 교사 | 문제 관리 |
| `GET` | `/questions` | 교사/학생 | 1~10번 문제 목록 |
| `POST` | `/rooms` | 교사 | 방 생성 |
| `PATCH` | `/rooms/{roomId}/start` | 교사 | 게임 시작 |
| `POST` | `/rooms/{roomId}/teams` | 교사 | 팀과 팀 PIN 생성 |
| `GET` | `/rooms/{roomId}/teams` | 교사 | 모둠 현황 조회 |
| `GET` | `/teams/{teamId}/progress` | 해당 팀/교사 | 팀 풀이 상태 조회 |
| `GET` | `/teams/{teamId}/score` | 해당 팀/교사 | 맞힌 문제 수 조회 |
| `GET` | `/teams/{teamId}/remaining` | 해당 팀/교사 | 남은 문제 수 조회 |
| `GET` | `/teams/{teamId}/answers/{questionId}` | 해당 팀/교사 | 제출·수정 횟수 조회 |
| `POST` | `/teams/{teamId}/answers/{questionId}` | 해당 팀 학생 | 단건 답안 제출(호환용) |
| `POST` | `/teams/{teamId}/answers/batch` | 해당 팀 학생 | 답안 일괄 채점 |
| `GET` | `/rooms/{roomId}/ranking` | 해당 방 학생/교사 | 순위 조회 |

학생 토큰으로 다른 팀의 진행 상태/제출 API나 다른 방의 순위 API에 접근하면 `403`입니다.

## 교사 흐름

### 문제 등록

```http
POST /questions
Authorization: Bearer {teacherToken}
Content-Type: application/json

{
  "questionNumber": 1,
  "answer": "Python",
  "maxSubmitCount": 3
}
```

`maxSubmitCount`가 난이도별 최대 시도 횟수입니다. 1 이상의 값을 문제마다 다르게 지정할 수
있습니다. 응답과 `GET /questions`에는 정답 `answer`가 노출되지 않습니다.

```json
{"id": 1, "questionNumber": 1, "maxSubmitCount": 3}
```

게임 시작 시 문제 번호가 정확히 1번부터 10번까지 존재해야 합니다.

### 방과 팀 생성

```http
POST /rooms
Authorization: Bearer {teacherToken}
```

```json
{"id": 1, "pin": "482193", "started": false}
```

```http
POST /rooms/1/teams
Authorization: Bearer {teacherToken}
Content-Type: application/json

{"teamName": "파이썬팀"}
```

```json
{
  "id": 7,
  "name": "파이썬팀",
  "pin": "583021",
  "currentCount": 0,
  "submissionRound": 0,
  "finished": false
}
```

방 PIN은 방 식별용이고, 팀 PIN은 학생의 팀 입장/로그인용입니다.
기존에 적혀 있던 학생용 `POST /rooms/{pin}/teams`는 사용하지 않습니다. 선생님이
`POST /rooms/{roomId}/teams`로 모둠을 만들고, 학생이 그 모둠 PIN으로
`POST /auth/student`에 로그인합니다. 모둠 생성 응답에는 입장에 필요한 `pin`과
일괄 제출 상태 확인용 `submissionRound`가 추가되어 있습니다.

모둠 현황은 선생님 토큰으로 `GET /rooms/{roomId}/teams`에서 조회합니다.

```json
[
  {"id": 7, "name": "파이썬팀", "currentCount": 0, "finished": false}
]
```

```http
PATCH /rooms/1/start
Authorization: Bearer {teacherToken}
```

## 학생 문제 화면과 이동

기존 명세의 맞힌 문제 수, 남은 문제 수, 제출·수정 횟수 조회도 각각 사용할 수 있습니다.

```http
GET /teams/7/score
GET /teams/7/remaining
GET /teams/7/answers/1
Authorization: Bearer {studentToken}
```

응답은 순서대로 `{"currentCount": 7}`, `{"remainingCount": 3}`,
`{"submitCount": 2, "modifyCount": 1}`입니다. `remainingCount`는 전체 등록 문제 수에서
맞힌 문제 수를 뺀 값입니다. 아직 답을 제출하지 않은 문항의 횟수 조회는 `404`입니다.

처음에는 `GET /questions`의 `questionNumber` 순서대로 1번부터 10번까지 보여 줍니다.
Enter 입력과 문항 번호 클릭은 프론트엔드의 현재 문항 인덱스만 변경합니다. Enter로 이동해도
채점 요청을 보내지 말고, 화면의 단일 제출 버튼을 눌렀을 때만 일괄 제출합니다.

초기 상태와 재접속 복원은 다음 API를 사용합니다.

```http
GET /teams/7/progress
Authorization: Bearer {studentToken}
```

아래 JSON은 `questions` 중 한 문항만 보여 주는 발췌 예시입니다. 실제 응답에는 모든
등록 문항이 포함되며, 전체 응답 예시는 [API 명세서](./API_SPEC.md#풀이-상태와-조회)에 있습니다.

```json
{
  "teamId": 7,
  "submissionRound": 1,
  "correctCount": 7,
  "totalQuestions": 10,
  "finished": false,
  "questions": [
    {
      "questionId": 1,
      "questionNumber": 1,
      "status": "CORRECT",
      "submittedAnswer": "Python",
      "submitCount": 1,
      "wrongCount": 0,
      "maxSubmitCount": 3,
      "remainingAttempts": 2,
      "locked": true
    }
  ],
  "rotationQuestionIds": [2, 3],
  "nextQuestionId": 2
}
```

상태 값의 의미는 다음과 같습니다.

| status | 의미 | 다시 제출 가능 |
| --- | --- | --- |
| `UNSUBMITTED` | 빈칸 또는 아직 제출하지 않음 | 예 |
| `WRONG` | 제출했지만 오답이며 기회가 남음 | 예 |
| `CORRECT` | 정답 | 아니요 |
| `EXHAUSTED` | 오답이며 최대 시도 횟수 소진 | 아니요 |

`wrongCount`는 오답을 실제로 채점한 경우에만 증가합니다. 빈칸/미제출은 `submitCount`와
`wrongCount` 모두 증가하지 않습니다. `locked: true`인 문항 입력은 비활성화합니다.

## 단일 버튼 일괄 제출

```http
POST /teams/7/answers/batch
Authorization: Bearer {studentToken}
Content-Type: application/json
```

```json
{
  "answers": [
    {"questionId": 1, "submittedAnswer": "Python"},
    {"questionId": 2, "submittedAnswer": ""},
    {"questionId": 3, "submittedAnswer": null}
  ]
}
```

- 최대 10개 문항을 한 요청에 보냅니다.
- 빈 문자열, 공백 또는 `null`은 미제출로 처리되어 횟수가 증가하지 않습니다.
- 이미 `CORRECT` 또는 `EXHAUSTED`인 문항은 재채점하지 않습니다.
- 응답은 진행 상태와 동일한 필드에 이번 요청에서 실제 채점한 `gradedCount`가 추가됩니다.
- 요청 처리 중 제출 버튼을 비활성화해 중복 클릭을 막습니다.

첫 제출 후에는 응답의 `rotationQuestionIds` 순서대로 미제출/오답 문항만 순환시킵니다.
정답 및 횟수 소진 문항은 로테이션에서 제외됩니다. 다음 문항은 `nextQuestionId`를 사용하며,
목록이 비면 `null`입니다.

모든 문항이 정답이면 `finished: true`가 됩니다. 횟수를 소진한 문항이 있다면 로테이션은
끝날 수 있지만 `finished`는 `false`일 수 있으므로 두 값을 구분해야 합니다.

기존 단건 제출 API `/teams/{teamId}/answers/{questionId}`는 호환 목적으로만 남아 있으며
deprecated 상태입니다. 응답은 제공된 명세와 같이 `id`, `submittedAnswer`, `correct`,
`submitCount`, `modifyCount`만 포함합니다. 오답 횟수는 진행 상태 API의 `wrongCount`에서
확인합니다. 새 프론트엔드는 일괄 제출 API를 사용합니다.

문제 삭제는 성공 시 `200`과 빈 객체 `{}`를 반환합니다. 존재하지 않는 문제는 `404`,
이미 시작된 방에 다시 시작 요청을 보내면 `400`입니다.

## 순위

```http
GET /rooms/1/ranking
Authorization: Bearer {token}
```

완료 팀 우선/완료 시간순, 미완료 팀은 정답 수 내림차순으로 정렬합니다. WebSocket은 아직
없으므로 순위 화면은 2초 이상의 간격으로 폴링하고 백그라운드 탭에서는 중지합니다.

## 프론트엔드 체크리스트

- [ ] API 주소를 `VITE_API_BASE_URL` 또는 `NEXT_PUBLIC_API_BASE_URL`로 관리
- [ ] 로그인 후 모든 요청에 Bearer 토큰 첨부
- [ ] 방 PIN, 팀 PIN, 학번을 문자열로 보관
- [ ] Enter/문항 클릭은 이동만 수행하고 단일 제출 버튼에서 일괄 채점
- [ ] 상태별 표시: 미제출/오답/정답/기회 소진
- [ ] `rotationQuestionIds`, `nextQuestionId`로 재도전 순서 처리
- [ ] `remainingAttempts`와 문제별 최대 횟수 표시
- [ ] `locked` 문항 비활성화
- [ ] `401` 재로그인, `403` 권한 오류, `message` 사용자 표시

전체 기계 판독 계약은 [openapi.json](./openapi.json)을 사용합니다.
