from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ApiModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class QuestionRequest(ApiModel):
    question_number: int = Field(alias="questionNumber", ge=1)
    answer: str
    max_submit_count: int = Field(alias="maxSubmitCount", ge=1)

    @field_validator("answer")
    @classmethod
    def answer_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("정답은 필수입니다.")
        return value


class QuestionResponse(ApiModel):
    id: int
    question_number: int = Field(alias="questionNumber")
    max_submit_count: int = Field(alias="maxSubmitCount")


class RoomResponse(ApiModel):
    id: int
    pin: str
    started: bool


class TeacherLoginRequest(ApiModel):
    access_code: str = Field(alias="accessCode", min_length=1)


class StudentLoginRequest(ApiModel):
    team_pin: str = Field(alias="teamPin", min_length=6, max_length=6)
    student_number: str = Field(alias="studentNumber", min_length=1)


class AuthTokenResponse(ApiModel):
    access_token: str = Field(alias="accessToken")
    token_type: str = Field(default="bearer", alias="tokenType")
    role: str
    expires_in: int = Field(alias="expiresIn")
    student_id: int | None = Field(default=None, alias="studentId")
    team_id: int | None = Field(default=None, alias="teamId")


class TeamJoinRequest(ApiModel):
    team_name: str = Field(alias="teamName")

    @field_validator("team_name")
    @classmethod
    def team_name_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("모둠 이름은 필수입니다.")
        return value.strip()


class TeamResponse(ApiModel):
    id: int
    name: str
    pin: str
    current_count: int = Field(alias="currentCount")
    submission_round: int = Field(alias="submissionRound")
    finished: bool


class TeamSummaryResponse(ApiModel):
    id: int
    name: str
    current_count: int = Field(alias="currentCount")
    finished: bool


class StudentResponse(ApiModel):
    id: int
    student_number: str = Field(alias="studentNumber")
    team_id: int = Field(alias="teamId")


class AnswerSubmitRequest(ApiModel):
    submitted_answer: str = Field(alias="submittedAnswer")

    @field_validator("submitted_answer")
    @classmethod
    def submitted_answer_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("답은 필수입니다.")
        return value


class SingleAnswerResponse(ApiModel):
    id: int
    submitted_answer: str = Field(alias="submittedAnswer")
    correct: bool
    submit_count: int = Field(alias="submitCount")
    modify_count: int = Field(alias="modifyCount")


class TeamScoreResponse(ApiModel):
    current_count: int = Field(alias="currentCount")


class RemainingQuestionsResponse(ApiModel):
    remaining_count: int = Field(alias="remainingCount")


class AnswerCountsResponse(ApiModel):
    submit_count: int = Field(alias="submitCount")
    modify_count: int = Field(alias="modifyCount")


class AnswerStatus(StrEnum):
    UNSUBMITTED = "UNSUBMITTED"
    WRONG = "WRONG"
    CORRECT = "CORRECT"
    EXHAUSTED = "EXHAUSTED"


class BatchAnswerItem(ApiModel):
    question_id: int = Field(alias="questionId", ge=1)
    submitted_answer: str | None = Field(default=None, alias="submittedAnswer")


class BatchAnswerSubmitRequest(ApiModel):
    answers: list[BatchAnswerItem] = Field(default_factory=list, max_length=10)

    @model_validator(mode="after")
    def question_ids_must_be_unique(self) -> "BatchAnswerSubmitRequest":
        ids = [answer.question_id for answer in self.answers]
        if len(ids) != len(set(ids)):
            raise ValueError("같은 문제를 중복 제출할 수 없습니다.")
        return self


class QuestionProgressResponse(ApiModel):
    question_id: int = Field(alias="questionId")
    question_number: int = Field(alias="questionNumber")
    status: AnswerStatus
    submitted_answer: str | None = Field(alias="submittedAnswer")
    submit_count: int = Field(alias="submitCount")
    wrong_count: int = Field(alias="wrongCount")
    max_submit_count: int = Field(alias="maxSubmitCount")
    remaining_attempts: int = Field(alias="remainingAttempts")
    locked: bool


class TeamProgressResponse(ApiModel):
    team_id: int = Field(alias="teamId")
    submission_round: int = Field(alias="submissionRound")
    correct_count: int = Field(alias="correctCount")
    total_questions: int = Field(alias="totalQuestions")
    finished: bool
    questions: list[QuestionProgressResponse]
    rotation_question_ids: list[int] = Field(alias="rotationQuestionIds")
    next_question_id: int | None = Field(alias="nextQuestionId")


class BatchAnswerSubmitResponse(TeamProgressResponse):
    graded_count: int = Field(alias="gradedCount")


class RankingResponse(ApiModel):
    rank: int
    team_name: str = Field(alias="teamName")
    current_count: int = Field(alias="currentCount")
    finished: bool
    finished_at: datetime | None = Field(alias="finishedAt")
