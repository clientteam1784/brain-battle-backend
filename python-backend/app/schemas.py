from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class AnswerResponse(ApiModel):
    id: int
    submitted_answer: str = Field(alias="submittedAnswer")
    correct: bool
    submit_count: int = Field(alias="submitCount")
    modify_count: int = Field(alias="modifyCount")


class RankingResponse(ApiModel):
    rank: int
    team_name: str = Field(alias="teamName")
    current_count: int = Field(alias="currentCount")
    finished: bool
    finished_at: datetime | None = Field(alias="finishedAt")
