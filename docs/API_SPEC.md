# Brain Battle 백엔드 API 명세서

현재 구현된 **19개 API 전체**를 정리한 문서입니다. 기준은 이 저장소의
`app/api.py`, `app/schemas.py`, `app/services.py`, `app/auth.py`, `app/exceptions.py`입니다.
사람이 읽는 상세 계약은 이 문서, 프론트 화면 흐름은 [연동 가이드](./FRONTEND_API_GUIDE.md),
자료형과 필수 필드의 기계 판독 계약은 [OpenAPI JSON](./openapi.json)을 참고합니다.

## 목차

- [공통 규칙](#공통-규칙)
- [API 전체 목록](#api-전체-목록)
- [오류 응답](#오류-응답)
- [상태 확인](#상태-확인)
- [로그인](#로그인)
- [문제 관리](#문제-관리)
- [방 관리](#방-관리)
- [모둠 및 학생 관리](#모둠-및-학생-관리)
- [풀이 상태와 조회](#풀이-상태와-조회)
- [답안 제출](#답안-제출)
- [순위 조회](#순위-조회)
- [프론트엔드 연동 순서](#프론트엔드-연동-순서)
- [기존 명세에서 정정한 부분](#기존-명세에서-정정한-부분)

## 공통 규칙

| 항목 | 계약 |
| --- | --- |
| 로컬 base URL | `http://localhost:8000` |
| 운영 base URL | 아직 확정된 배포 주소 없음. 실제 배포 시 HTTPS 주소 설정 |
| API prefix | 없음. `/api/questions` 대신 `/questions` 사용 |
| 요청·응답 | JSON. body가 있는 요청은 `Content-Type: application/json` |
| 인증 | `/health`, `/auth/teacher`, `/auth/student` 외 모든 API에 Bearer 토큰 필요 |
| Swagger UI | 서버의 `/docs` |
| 실행 중인 서버의 OpenAPI | 서버의 `/openapi.json` |
| ID | JSON 정수. URL에서는 실제 ID 숫자로 치환 |
| PIN·학번 | 문자열. 방 PIN과 모둠 PIN은 서로 다른 값 |
| 목록 | 데이터가 없으면 `[]` |
| 날짜 | `finishedAt`은 타임존 오프셋 없는 ISO 8601 문자열 또는 `null` |

```http
Authorization: Bearer {accessToken}
Content-Type: application/json
```

GET 요청에는 body가 없습니다. body가 없는 POST/PATCH도 body를 생략할 수 있으며 `{}`를
보내도 됩니다. `roomId: 1`, `teamId: 7`, `questionId: 2`는 JSON body가 아니라 URL의
경로 변수입니다. 이 문서는 코드의 이름대로 `{room_id}`, `{team_id}`, `{question_id}`를
표기합니다. 예를 들어 `/teams/{team_id}/score`의 실제 요청은 `/teams/7/score`입니다.

`studentNumber`만 학생 등록 API의 query parameter입니다. 응답 JSON의 필드는 camelCase입니다.
교사 토큰에는 특정 방 소유권 제한이 없고, 학생 토큰은 로그인한 모둠과 그 모둠의 방으로
접근 범위가 제한됩니다. 학생 로그인은 모둠 PIN과 학번을 사용하는 입장 방식이며 학번만으로
별도의 신원 인증을 수행하지는 않습니다.

## API 전체 목록

| Method | Path | 권한 | 기능 |
| --- | --- | --- | --- |
| GET | `/health` | 공개 | 서버 상태 확인 |
| POST | `/auth/teacher` | 공개 | 교사 로그인 |
| POST | `/auth/student` | 공개 | 모둠 PIN으로 학생 로그인 |
| POST | `/questions` | 교사 | 문제 등록 |
| GET | `/questions` | 교사·학생 | 문제 목록 조회 |
| PATCH | `/questions/{question_id}` | 교사 | 문제 수정 |
| DELETE | `/questions/{question_id}` | 교사 | 문제 삭제 |
| POST | `/rooms` | 교사 | 방 생성 |
| PATCH | `/rooms/{room_id}/start` | 교사 | 게임 시작 |
| POST | `/rooms/{room_id}/teams` | 교사 | 모둠 및 모둠 PIN 생성 |
| GET | `/rooms/{room_id}/teams` | 교사 | 모둠 현황 조회 |
| POST | `/teams/{team_id}/students` | 교사 | 학생 사전 등록 |
| GET | `/teams/{team_id}/progress` | 교사·해당 모둠 학생 | 전체 풀이 상태 조회 |
| GET | `/teams/{team_id}/score` | 교사·해당 모둠 학생 | 맞힌 문제 수 조회 |
| GET | `/teams/{team_id}/remaining` | 교사·해당 모둠 학생 | 남은 문제 수 조회 |
| GET | `/teams/{team_id}/answers/{question_id}` | 교사·해당 모둠 학생 | 제출·수정 횟수 조회 |
| POST | `/teams/{team_id}/answers/batch` | 해당 모둠 학생 | 답안 일괄 채점 |
| POST | `/teams/{team_id}/answers/{question_id}` | 해당 모둠 학생 | 단건 제출, deprecated |
| GET | `/rooms/{room_id}/ranking` | 교사·해당 방 학생 | 모둠별 정답 수 및 순위 조회 |

## 오류 응답

### 공통 인증·권한 오류

아래 오류는 인증이 필요한 모든 API에 적용됩니다. 개별 API의 오류 표에서는 중복하여
나열하지 않습니다. 인증이나 모둠 접근 확인이 먼저 실패하면 대상 조회의 `404` 대신
`401` 또는 `403`이 반환될 수 있습니다.

| HTTP status | message |
| --- | --- |
| 401 | `인증이 필요합니다.` |
| 401 | `유효하지 않거나 만료된 인증 토큰입니다.` |
| 401 | `유효하지 않은 사용자 역할입니다.` |
| 403 | `선생님 권한이 필요합니다.` |
| 403 | `학생 권한이 필요합니다.` |
| 403 | `다른 조의 정보에는 접근할 수 없습니다.` |
| 403 | `다른 방의 정보에는 접근할 수 없습니다.` |

기본 오류 body는 다음 형식입니다.

```json
{"message": "인증이 필요합니다."}
```

일부 교사 API는 기존 명세에 따라 `status` 필드도 반환합니다.

```json
{"status": 404, "message": "존재하지 않는 문제입니다."}
```

이하 오류 표의 **status 필드**가 `있음`이면 위 두 번째 형식, `없음`이면 첫 번째 형식입니다.
HTTP 응답 상태를 항상 기준으로 판단하고 body의 `status`는 선택적으로 읽습니다.

### 입력값 검증

입력값 검증 실패는 `400`이며 첫 번째 검증 오류의 `message`가 반환됩니다. `/questions`
경로의 입력값 오류는 `status: 400`도 포함하고, 다른 경로는 `message`만 반환합니다.
필수 필드 누락, 자료형 오류, 길이 초과 등의 메시지는 Pydantic의 메시지가 될 수 있습니다.
현재 자동 생성 OpenAPI에는 FastAPI 기본 검증 응답 `422`가 표시될 수 있지만 실제
검증 오류 handler는 `400`을 반환합니다. 실제 오류 형식은 이 문서와 서버 응답을 따릅니다.
처리되지 않은 서버·DB 오류까지 JSON `message` 형식으로 보장하지는 않습니다.

## 상태 확인

### `GET /health`

인증: 공개. 요청 body 없음.

성공: `200`

```json
{"status": "ok"}
```

서버 응답 여부를 확인합니다. DB 연결 상태까지 검사하는 API는 아닙니다.

## 로그인

### `POST /auth/teacher`

인증: 공개.

요청:

```json
{"accessCode": "교사용 접근 코드"}
```

`accessCode`: 필수 문자열, 길이 1 이상. 서버의 `TEACHER_ACCESS_CODE`와 일치해야 합니다.

성공: `200`

```json
{
  "accessToken": "<교사 JWT>",
  "tokenType": "bearer",
  "role": "teacher",
  "expiresIn": 28800,
  "studentId": null,
  "teamId": null
}
```

| HTTP status | message | status 필드 |
| --- | --- | --- |
| 401 | `선생님 인증 코드가 올바르지 않습니다.` | 없음 |

토큰 유효 시간은 `JWT_EXPIRE_MINUTES` 설정으로 변경됩니다. 기본은 480분(8시간)이며
`expiresIn`의 단위는 초입니다. 별도의 refresh token·로그아웃 API는 없습니다.

### `POST /auth/student`

인증: 공개. 방 PIN이 아닌 **모둠 PIN**을 사용합니다.

요청:

```json
{"teamPin": "583021", "studentNumber": "20260001"}
```

| 필드 | 자료형 | 조건 |
| --- | --- | --- |
| teamPin | string | 필수, 길이 정확히 6 |
| studentNumber | string | 필수, 공백만 있는 값 금지 |

성공: `200`

```json
{
  "accessToken": "<학생 JWT>",
  "tokenType": "bearer",
  "role": "student",
  "expiresIn": 28800,
  "studentId": 15,
  "teamId": 7
}
```

같은 모둠의 같은 학번으로 재로그인하면 기존 학생을 사용합니다. 처음 로그인한 학번은
해당 모둠에 자동 등록됩니다. 로그인 응답에 `roomId`는 없습니다. 프론트엔드는 교사가
진행하는 방의 ID를 별도로 공유·보관해야 방 순위 API를 호출할 수 있습니다.

| HTTP status | message | status 필드 |
| --- | --- | --- |
| 401 | `존재하지 않는 조 PIN입니다.` | 없음 |
| 400 | `학번은 필수입니다.` | 없음 |
| 409 | `학생 등록 중 충돌이 발생했습니다.` | 없음 |

## 문제 관리

문제는 현재 방별로 분리되지 않고 전체 목록으로 관리됩니다. 게임 시작 전 문제 번호가
정확히 1~10번 존재해야 합니다. 문제 응답에는 정답 `answer`가 포함되지 않습니다.

### `POST /questions`

인증: 교사.

요청:

```json
{"questionNumber": 1, "answer": "사과", "maxSubmitCount": 3}
```

| 필드 | 자료형 | 조건 |
| --- | --- | --- |
| questionNumber | integer | 필수, 1 이상, 전체 목록에서 유일 |
| answer | string | 필수, 공백만 있는 값 금지 |
| maxSubmitCount | integer | 필수, 1 이상, 첫 제출을 포함한 최대 시도 횟수 |

성공: `200`

```json
{"id": 1, "questionNumber": 1, "maxSubmitCount": 3}
```

| HTTP status | message | status 필드 |
| --- | --- | --- |
| 400 | `문제 번호는 1 이상이어야 합니다.` | 있음 |
| 400 | `정답은 필수입니다.` | 있음 |
| 400 | `최대 제출 횟수는 1 이상이어야 합니다.` | 있음 |
| 400 | `이미 존재하는 문제 번호입니다.` | 없음 |

난이도별 시도 횟수는 교사가 문제마다 `maxSubmitCount`를 다르게 지정하여 설정합니다.
난이도 이름을 저장하거나 횟수를 자동 계산하는 필드는 없습니다. 예를 들어 값이 3이면
최초 제출 1회와 추가 제출 최대 2회가 가능합니다.

### `GET /questions`

인증: 교사·학생. 요청 body 없음.

성공: `200`. 문제 번호 오름차순.

```json
[
  {"id": 1, "questionNumber": 1, "maxSubmitCount": 3},
  {"id": 2, "questionNumber": 2, "maxSubmitCount": 5}
]
```

문제가 없으면 `[]`입니다. 문제 본문·이미지 등의 콘텐츠 필드는 현재 API에 없습니다.
인증·입력값 공통 오류 외 별도 비즈니스 오류는 없습니다.

### `PATCH /questions/{question_id}`

인증: 교사. 예: `/questions/1`.

요청:

```json
{"questionNumber": 1, "answer": "바나나", "maxSubmitCount": 5}
```

세 필드를 모두 보내는 수정입니다. 부분 필드만 보내는 PATCH가 아닙니다. 조건은 등록과 같습니다.

성공: `200`

```json
{"id": 1, "questionNumber": 1, "maxSubmitCount": 5}
```

| HTTP status | message | status 필드 |
| --- | --- | --- |
| 404 | `존재하지 않는 문제입니다.` | 있음 |
| 400 | 등록 API와 동일한 입력값 오류 | 있음 |
| 400 | `이미 존재하는 문제 번호입니다.` | 없음 |

### `DELETE /questions/{question_id}`

인증: 교사. 예: `/questions/1`. 요청 body 없음.

성공: **`200`**, JSON body 있음.

```json
{}
```

| HTTP status | message | status 필드 |
| --- | --- | --- |
| 404 | `존재하지 않는 문제입니다.` | 있음 |

## 방 관리

### `POST /rooms`

인증: 교사. 요청 body 없음 또는 `{}`.

성공: `200`

```json
{"id": 1, "pin": "123456", "started": false}
```

`pin`은 방 식별용 6자리 문자열입니다. 학생 입장에는 모둠 생성 응답의 PIN을 사용합니다.

| HTTP status | message | status 필드 |
| --- | --- | --- |
| 500 | `방 생성에 실패했습니다.` | 있음 |

위 500 응답은 처리된 PIN 생성·유니크 제약 오류의 응답입니다.

### `PATCH /rooms/{room_id}/start`

인증: 교사. 예: `/rooms/1/start`. 요청 body 없음 또는 `{}`.

성공: `200`

```json
{"id": 1, "pin": "123456", "started": true}
```

| HTTP status | message | status 필드 |
| --- | --- | --- |
| 404 | `존재하지 않는 방입니다.` | 있음 |
| 400 | `이미 시작된 게임입니다.` | 있음 |
| 400 | `게임 시작 전 1번부터 10번까지 문제를 등록해야 합니다.` | 없음 |

## 모둠 및 학생 관리

### `POST /rooms/{room_id}/teams`

인증: **교사**. 예: `/rooms/1/teams`.

요청:

```json
{"teamName": "1모둠"}
```

`teamName`: 필수 문자열. 공백만 있는 값은 금지하며 앞뒤 공백을 제거해 저장합니다.
같은 방에서는 모둠 이름이 유일해야 합니다.

성공: `200`

```json
{
  "id": 7,
  "name": "1모둠",
  "pin": "583021",
  "currentCount": 0,
  "submissionRound": 0,
  "finished": false
}
```

이 응답의 `pin`을 해당 모둠 학생들에게 전달합니다. `submissionRound`는 성공한 일괄
제출 요청 횟수입니다. 선생님이 만드는 API이며 학생 토큰으로 생성할 수 없습니다.

| HTTP status | message | status 필드 |
| --- | --- | --- |
| 404 | `존재하지 않는 방입니다.` | 없음 |
| 400 | `이미 존재하는 모둠 이름입니다.` | 없음 |
| 400 | `모둠 이름은 필수입니다.` | 없음 |
| 400 | `이미 존재하는 모둠 이름 또는 PIN입니다.` | 없음 |
| 503 | `조 PIN을 생성하지 못했습니다. 다시 시도해주세요.` | 없음 |

### `GET /rooms/{room_id}/teams`

인증: 교사. 예: `/rooms/1/teams`. 요청 body 없음.

성공: `200`. 모둠 ID 오름차순. 모둠 PIN은 이 목록에 노출되지 않습니다.

```json
[
  {"id": 7, "name": "1모둠", "currentCount": 7, "finished": false},
  {"id": 8, "name": "2모둠", "currentCount": 10, "finished": true}
]
```

| HTTP status | message | status 필드 |
| --- | --- | --- |
| 404 | `존재하지 않는 방입니다.` | 있음 |

### `POST /teams/{team_id}/students`

인증: 교사. 학생 사전 등록용이며 JWT를 발급하는 API가 아닙니다.

요청 예:

```http
POST /teams/7/students?studentNumber=20260001
Authorization: Bearer {teacherToken}
```

body 없음. `studentNumber`는 필수 query 문자열입니다. 실제 요청 시 URL encoding을 적용합니다.

성공: `200`

```json
{"id": 15, "studentNumber": "20260001", "teamId": 7}
```

같은 모둠·학번이 이미 등록되어 있으면 기존 학생을 반환합니다. 학생 로그인 시에도 자동
등록하므로 반드시 먼저 호출해야 하는 API는 아닙니다.

| HTTP status | message | status 필드 |
| --- | --- | --- |
| 404 | `존재하지 않는 모둠입니다.` | 없음 |
| 400 | `학번은 필수입니다.` | 없음 |
| 409 | `학생 등록 중 충돌이 발생했습니다.` | 없음 |

## 풀이 상태와 조회

### `GET /teams/{team_id}/progress`

인증: 교사·해당 모둠 학생. 예: `/teams/7/progress`. 요청 body 없음.

성공: `200`. 다음은 1번 정답, 2번 오답, 3~10번 미제출인 경우의 전체 응답 예입니다.
`questions`는 등록된 모든 문항을 문제 번호순으로 포함합니다.

```json
{
  "teamId": 7,
  "submissionRound": 1,
  "correctCount": 1,
  "totalQuestions": 10,
  "finished": false,
  "questions": [
    {"questionId": 1, "questionNumber": 1, "status": "CORRECT", "submittedAnswer": "사과", "submitCount": 1, "wrongCount": 0, "maxSubmitCount": 3, "remainingAttempts": 2, "locked": true},
    {"questionId": 2, "questionNumber": 2, "status": "WRONG", "submittedAnswer": "오답", "submitCount": 1, "wrongCount": 1, "maxSubmitCount": 3, "remainingAttempts": 2, "locked": false},
    {"questionId": 3, "questionNumber": 3, "status": "UNSUBMITTED", "submittedAnswer": null, "submitCount": 0, "wrongCount": 0, "maxSubmitCount": 3, "remainingAttempts": 3, "locked": false},
    {"questionId": 4, "questionNumber": 4, "status": "UNSUBMITTED", "submittedAnswer": null, "submitCount": 0, "wrongCount": 0, "maxSubmitCount": 3, "remainingAttempts": 3, "locked": false},
    {"questionId": 5, "questionNumber": 5, "status": "UNSUBMITTED", "submittedAnswer": null, "submitCount": 0, "wrongCount": 0, "maxSubmitCount": 3, "remainingAttempts": 3, "locked": false},
    {"questionId": 6, "questionNumber": 6, "status": "UNSUBMITTED", "submittedAnswer": null, "submitCount": 0, "wrongCount": 0, "maxSubmitCount": 3, "remainingAttempts": 3, "locked": false},
    {"questionId": 7, "questionNumber": 7, "status": "UNSUBMITTED", "submittedAnswer": null, "submitCount": 0, "wrongCount": 0, "maxSubmitCount": 3, "remainingAttempts": 3, "locked": false},
    {"questionId": 8, "questionNumber": 8, "status": "UNSUBMITTED", "submittedAnswer": null, "submitCount": 0, "wrongCount": 0, "maxSubmitCount": 3, "remainingAttempts": 3, "locked": false},
    {"questionId": 9, "questionNumber": 9, "status": "UNSUBMITTED", "submittedAnswer": null, "submitCount": 0, "wrongCount": 0, "maxSubmitCount": 3, "remainingAttempts": 3, "locked": false},
    {"questionId": 10, "questionNumber": 10, "status": "UNSUBMITTED", "submittedAnswer": null, "submitCount": 0, "wrongCount": 0, "maxSubmitCount": 3, "remainingAttempts": 3, "locked": false}
  ],
  "rotationQuestionIds": [2, 3, 4, 5, 6, 7, 8, 9, 10],
  "nextQuestionId": 2
}
```

| 필드 | 자료형 | 의미 |
| --- | --- | --- |
| teamId | integer | 모둠 ID |
| submissionRound | integer | 성공한 일괄 제출 횟수. 빈 일괄 제출도 증가 |
| correctCount | integer | 현재 맞힌 문제 수 |
| totalQuestions | integer | 현재 전체 등록 문제 수 |
| finished | boolean | 모든 등록 문제를 맞혔는지 |
| questions | array | 문제별 상태 |
| rotationQuestionIds | integer[] | 재도전 가능한 문항 ID. 문제 번호순 |
| nextQuestionId | integer 또는 null | 로테이션 목록의 첫 ID. 목록이 비면 null |
| questions[].questionId | integer | 실제 문제 ID. questionNumber와 같다고 가정하지 않기 |
| questions[].questionNumber | integer | 화면 표시용 문제 번호 |
| questions[].status | string | 아래 상태 표 참고 |
| questions[].submittedAnswer | string 또는 null | 마지막으로 채점된 답. 미제출은 null |
| questions[].submitCount | integer | 실제 채점한 제출 수 |
| questions[].wrongCount | integer | 오답으로 채점한 수 |
| questions[].maxSubmitCount | integer | 최초 제출을 포함한 최대 시도 횟수 |
| questions[].remainingAttempts | integer | `max(maxSubmitCount - submitCount, 0)` |
| questions[].locked | boolean | 정답 또는 횟수 소진이면 true |

| status | 의미 | 로테이션 포함 |
| --- | --- | --- |
| UNSUBMITTED | 아직 채점된 답안 없음 | 예 |
| WRONG | 오답이며 제출 기회 남음 | 예 |
| CORRECT | 정답 | 아니요 |
| EXHAUSTED | 오답이며 제출 횟수 소진 | 아니요 |

`remainingAttempts`가 양수여도 `CORRECT` 문항은 잠겨 있습니다. 다시 제출할 수 있는지는
`locked`로 판단합니다. `remainingCount`와 달리 로테이션은 기회가 소진된 문항을 제외합니다.
모든 미해결 문항의 기회가 소진되면 로테이션은 비어 있어도 `finished`는 false일 수 있습니다.
`nextQuestionId`는 서버가 사용자 커서를 저장한 값이 아니라 재도전 목록의 첫 문항입니다.

| HTTP status | message | status 필드 |
| --- | --- | --- |
| 404 | `존재하지 않는 모둠입니다.` | 없음 |

### `GET /teams/{team_id}/score`

인증: 교사·해당 모둠 학생. 예: `/teams/7/score`. 요청 body 없음.

성공: `200`

```json
{"currentCount": 7}
```

| HTTP status | message | status 필드 |
| --- | --- | --- |
| 404 | `존재하지 않는 모둠입니다.` | 없음 |

### `GET /teams/{team_id}/remaining`

인증: 교사·해당 모둠 학생. 예: `/teams/7/remaining`. 요청 body 없음.

성공: `200`

```json
{"remainingCount": 3}
```

`remainingCount = max(전체 등록 문제 수 - 맞힌 문제 수, 0)`. 제출 기회가 소진됐어도
못 맞힌 문제는 이 수에 포함됩니다. 재도전 가능한 문항 수는 `progress`의
`rotationQuestionIds.length`를 사용합니다.

| HTTP status | message | status 필드 |
| --- | --- | --- |
| 404 | `존재하지 않는 모둠입니다.` | 없음 |

### `GET /teams/{team_id}/answers/{question_id}`

인증: 교사·해당 모둠 학생. 예: `/teams/7/answers/1`. 요청 body 없음.

성공: `200`

```json
{"submitCount": 2, "modifyCount": 1}
```

`modifyCount`는 최초 채점 이후의 추가 채점 횟수입니다. 답이 이전 답과 같아도 재채점되면
증가합니다. 미제출인 경우 이 API는 0을 반환하지 않고 `404`를 반환합니다.
0을 포함한 전체 상태는 `progress`를 사용합니다.

| HTTP status | message | status 필드 |
| --- | --- | --- |
| 404 | `존재하지 않는 답안입니다.` | 없음 |

## 답안 제출

### `POST /teams/{team_id}/answers/batch`

인증: 해당 모둠 학생. 예: `/teams/7/answers/batch`. 단일 제출 버튼에서 호출합니다.

요청:

```json
{
  "answers": [
    {"questionId": 1, "submittedAnswer": "사과"},
    {"questionId": 2, "submittedAnswer": "오답"},
    {"questionId": 3, "submittedAnswer": ""},
    {"questionId": 4, "submittedAnswer": null}
  ]
}
```

| 필드 | 자료형 | 조건 |
| --- | --- | --- |
| answers | array | 최대 10개. 생략 시 빈 배열로 처리 |
| answers[].questionId | integer | 필수, 1 이상. 같은 ID 중복 금지 |
| answers[].submittedAnswer | string 또는 null | 생략·null·빈칸·공백은 이번 요청에서 미제출 |

성공: `200`. [progress](#get-teamsteam_idprogress)의 모든 필드에 `gradedCount`가 추가됩니다.
다음은 위 요청을 최초 제출했을 때의 응답입니다.

```json
{
  "teamId": 7,
  "submissionRound": 1,
  "correctCount": 1,
  "totalQuestions": 10,
  "finished": false,
  "gradedCount": 2,
  "questions": [
    {"questionId": 1, "questionNumber": 1, "status": "CORRECT", "submittedAnswer": "사과", "submitCount": 1, "wrongCount": 0, "maxSubmitCount": 3, "remainingAttempts": 2, "locked": true},
    {"questionId": 2, "questionNumber": 2, "status": "WRONG", "submittedAnswer": "오답", "submitCount": 1, "wrongCount": 1, "maxSubmitCount": 3, "remainingAttempts": 2, "locked": false},
    {"questionId": 3, "questionNumber": 3, "status": "UNSUBMITTED", "submittedAnswer": null, "submitCount": 0, "wrongCount": 0, "maxSubmitCount": 3, "remainingAttempts": 3, "locked": false},
    {"questionId": 4, "questionNumber": 4, "status": "UNSUBMITTED", "submittedAnswer": null, "submitCount": 0, "wrongCount": 0, "maxSubmitCount": 3, "remainingAttempts": 3, "locked": false},
    {"questionId": 5, "questionNumber": 5, "status": "UNSUBMITTED", "submittedAnswer": null, "submitCount": 0, "wrongCount": 0, "maxSubmitCount": 3, "remainingAttempts": 3, "locked": false},
    {"questionId": 6, "questionNumber": 6, "status": "UNSUBMITTED", "submittedAnswer": null, "submitCount": 0, "wrongCount": 0, "maxSubmitCount": 3, "remainingAttempts": 3, "locked": false},
    {"questionId": 7, "questionNumber": 7, "status": "UNSUBMITTED", "submittedAnswer": null, "submitCount": 0, "wrongCount": 0, "maxSubmitCount": 3, "remainingAttempts": 3, "locked": false},
    {"questionId": 8, "questionNumber": 8, "status": "UNSUBMITTED", "submittedAnswer": null, "submitCount": 0, "wrongCount": 0, "maxSubmitCount": 3, "remainingAttempts": 3, "locked": false},
    {"questionId": 9, "questionNumber": 9, "status": "UNSUBMITTED", "submittedAnswer": null, "submitCount": 0, "wrongCount": 0, "maxSubmitCount": 3, "remainingAttempts": 3, "locked": false},
    {"questionId": 10, "questionNumber": 10, "status": "UNSUBMITTED", "submittedAnswer": null, "submitCount": 0, "wrongCount": 0, "maxSubmitCount": 3, "remainingAttempts": 3, "locked": false}
  ],
  "rotationQuestionIds": [2, 3, 4, 5, 6, 7, 8, 9, 10],
  "nextQuestionId": 2
}
```

`gradedCount`는 이번 요청에서 실제 채점한 문항 수이며 정답·오답 모두 포함합니다.
잠긴 문항과 미제출 문항은 포함하지 않습니다.

채점 규칙:

- 시작된 방의 미완료 모둠만 제출할 수 있습니다.
- 앞뒤 공백과 영문 대소문자를 무시하여 정답을 비교합니다.
- 빈칸·null·요청에서 빠진 문항은 채점하지 않으며 기존 답안·상태도 지우지 않습니다.
- 실제 채점할 때 `submitCount`가 증가하고, 오답일 때만 `wrongCount`가 증가합니다.
- 첫 채점 이후 추가 채점 시 `modifyCount`가 증가합니다.
- 이미 정답이거나 횟수를 소진한 문항은 무시하며 재채점하지 않습니다.
- 빈 요청도 성공하면 `submissionRound`가 증가합니다.
- 모든 문제를 맞히면 `finished`가 true가 되고 완료 시간이 기록됩니다.
- 요청 자체에 멱등성 키는 없습니다. 제출 버튼은 요청 중 비활성화하고 자동 재시도에 주의합니다.

| HTTP status | message | status 필드 |
| --- | --- | --- |
| 404 | `존재하지 않는 모둠입니다.` | 없음 |
| 400 | `아직 게임이 시작되지 않았습니다.` | 없음 |
| 400 | `이미 모든 문제를 완료한 모둠입니다.` | 없음 |
| 400 | `같은 문제를 중복 제출할 수 없습니다.` | 없음 |
| 400 | `존재하지 않는 문제 ID가 포함되어 있습니다: [999]` | 없음 |
| 409 | `동일한 답안이 동시에 제출되었습니다. 다시 시도해주세요.` | 없음 |

10개 초과, 잘못된 자료형·ID 등은 공통 입력값 검증 오류 `400`입니다.
존재하지 않는 ID 오류의 숫자 목록은 요청에 따라 달라집니다.

### `POST /teams/{team_id}/answers/{question_id}`

인증: 해당 모둠 학생. 예: `/teams/7/answers/1`. **deprecated: 기존 연동 호환용**입니다.
새 화면은 위 일괄 제출 API를 사용합니다.

요청:

```json
{"submittedAnswer": "사과"}
```

`submittedAnswer`: 필수 문자열. 이 단건 API에서는 빈칸·null·공백만 있는 답안을 허용하지 않습니다.

성공: `200`

```json
{"id": 20, "submittedAnswer": "사과", "correct": true, "submitCount": 1, "modifyCount": 0}
```

이 API의 `id`는 문제 ID가 아닌 답안 ID입니다. 정답 비교와 횟수 계산은 일괄 제출과 같습니다.
단건 제출은 `submissionRound`를 증가시키지 않습니다. 이미 잠긴 문항을 제출하면
일괄 제출과 달리 아래 `400` 오류를 반환합니다.

| HTTP status | message | status 필드 |
| --- | --- | --- |
| 404 | `존재하지 않는 모둠입니다.` | 없음 |
| 404 | `존재하지 않는 문제입니다.` | 없음 |
| 400 | `아직 게임이 시작되지 않았습니다.` | 없음 |
| 400 | `이미 모든 문제를 완료한 모둠입니다.` | 없음 |
| 400 | `이미 정답을 맞힌 문제입니다.` | 없음 |
| 400 | `답안 제출 횟수를 초과했습니다.` | 없음 |
| 400 | `답은 필수입니다.` | 없음 |

## 순위 조회

### `GET /rooms/{room_id}/ranking`

인증: 교사·해당 방 학생. 예: `/rooms/1/ranking`. 요청 body 없음.

성공: `200`

```json
[
  {"rank": 1, "teamName": "2모둠", "currentCount": 10, "finished": true, "finishedAt": "2026-10-02T15:30:20"},
  {"rank": 2, "teamName": "1모둠", "currentCount": 7, "finished": false, "finishedAt": null}
]
```

같은 응답을 모둠별 정답 개수 화면과 현재 순위 화면에서 함께 사용합니다.

정렬 순서:

1. 모든 문제를 맞힌 완료 모둠 우선
2. 완료 모둠은 완료 시간 오름차순
3. 미완료 모둠은 맞힌 문제 수 내림차순
4. 나머지가 같으면 모둠 ID 오름차순

`rank`는 이 순서의 1부터 시작하는 순번이며 공동 순위를 계산하지 않습니다.
응답에 모둠 ID는 없으므로 ID가 필요한 화면은 교사용 모둠 현황 API를 함께 사용합니다.
실시간 이벤트·WebSocket은 없습니다. 순위 화면은 2초 이상의 간격으로 폴링하고
백그라운드 탭에서는 중지하는 방식을 권장합니다.

| HTTP status | message | status 필드 |
| --- | --- | --- |
| 404 | `존재하지 않는 방입니다.` | 없음 |

## 프론트엔드 연동 순서

1. 선생님: 교사 로그인 → 방 생성 → 1~10번 문제 등록 → 모둠 생성 및 모둠 PIN 전달 → 게임 시작.
2. 학생: 모둠 PIN·학번 로그인 → `teamId`와 토큰 보관 → 문제 목록·진행 상태 조회.
3. 첫 풀이: 1~10번 순서로 입력. Enter·문항 클릭은 화면 이동만 수행.
4. 단일 제출 버튼: `answers/batch` 호출 → 응답 상태·오답 수·남은 기회 표시.
5. 재도전: `rotationQuestionIds` 순서로 반복하고 잠긴 문항은 입력 비활성화.
6. 새로고침·재접속: `progress`로 채점된 답안과 상태 복원. 미제출 초안은 서버에 저장되지 않음.
7. 순위 화면: 보관한 `roomId`로 순위 조회. 토큰 만료의 `401`은 재로그인 처리.

문제 추가·수정·삭제는 전체 목록에 영향을 주므로 게임 중 교사의 문제 변경 시 화면과 점수가
달라질 수 있습니다. 현재 방별 문제 스냅샷·초안 저장·문항 이동 API는 없습니다.

## 기존 명세에서 정정한 부분

사용자가 확정한 흐름은 **선생님이 모둠을 생성하고 학생이 그 모둠 PIN으로 입장**하는 방식입니다.

| 기존 표기 | 현재 계약 |
| --- | --- |
| 학생 `POST /rooms/{pin}/teams` | 교사 `POST /rooms/{room_id}/teams` + 학생 `POST /auth/student` |
| 모둠 생성 응답에 PIN 없음 | 학생 입장에 필요한 `pin`, 일괄 제출 상태의 `submissionRound` 포함 |
| 문항별 제출 버튼 | 화면의 단일 제출 버튼에서 `answers/batch` 사용 |
| 단건 답안 제출 | 호환용 deprecated API로 유지 |
| 문제 삭제 `204` | `200`과 `{}` 반환 |
| 일부 조회 미구현 | 모둠 현황·score·remaining·제출/수정 횟수 모두 구현 |

노션 원문은 현재 연결된 워크스페이스에서 접근 불가이므로 최근 내용을 읽어 확인한 문서는
아닙니다. 이 문서는 앞서 제공된 request/response, 확정된 변경사항, 현재 코드에 근거합니다.
