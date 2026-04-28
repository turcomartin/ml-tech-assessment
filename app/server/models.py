import uuid
import pydantic


class LLMResponse(pydantic.BaseModel):
    summary: str
    action_items: list[str]


class AnalysisRecord(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        json_schema_extra={
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "summary": "The client discussed challenges with time management and prioritizing deep work alongside recurring meetings.",
                "action_items": [
                    "Block 9–11 AM daily for focused work and protect it from meetings.",
                    "Audit recurring meetings and cancel or delegate at least two.",
                    "Review progress with manager at the end of the week.",
                ],
            }
        }
    )

    id: uuid.UUID
    summary: str
    action_items: list[str]


class BatchRequest(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        json_schema_extra={
            "example": {
                "transcripts": [
                    "Coach: What's been your biggest challenge this week? Client: Staying focused — too many interruptions.",
                    "Coach: How are you tracking toward your Q2 goals? Client: Behind on two of them, mainly due to scope creep.",
                ]
            }
        }
    )

    transcripts: list[str]

    @pydantic.field_validator("transcripts")
    @classmethod
    def transcripts_must_be_non_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("transcripts list must not be empty")
        for i, t in enumerate(v):
            if not t.strip():
                raise ValueError(f"transcript at index {i} must not be blank")
        return v


class BatchResponse(pydantic.BaseModel):
    results: list[AnalysisRecord]
