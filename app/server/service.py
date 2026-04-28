import asyncio
import uuid

import openai
import pydantic

from app import ports, prompts
from app.server.models import AnalysisRecord, LLMResponse
from app.server.storage import InMemoryStorage


class RateLimitException(Exception):
    pass


class ServiceUnavailableException(Exception):
    pass


class AnalysisService:
    def __init__(self, llm: ports.LLm, storage: InMemoryStorage) -> None:
        self._llm = llm
        self._storage = storage

    def _build_user_prompt(self, transcript: str) -> str:
        return prompts.RAW_USER_PROMPT.format(transcript=transcript)

    def _call_llm(self, transcript: str) -> LLMResponse:
        user_prompt = self._build_user_prompt(transcript)
        try:
            return self._llm.run_completion(
                system_prompt=prompts.SYSTEM_PROMPT,
                user_prompt=user_prompt,
                dto=LLMResponse,
            )
        except openai.RateLimitError as e:
            raise RateLimitException(str(e)) from e
        except (openai.APIConnectionError, openai.APITimeoutError) as e:
            raise ServiceUnavailableException(str(e)) from e

    def analyze(self, transcript: str) -> AnalysisRecord:
        llm_response: LLMResponse = self._call_llm(transcript)
        record = AnalysisRecord(
            id=uuid.uuid4(),
            summary=llm_response.summary,
            action_items=llm_response.action_items,
        )
        self._storage.save(record)
        return record

    def get_analysis(self, record_id: uuid.UUID) -> AnalysisRecord | None:
        return self._storage.get(record_id)

    async def analyze_async(self, transcript: str) -> AnalysisRecord:
        loop = asyncio.get_running_loop()
        llm_response: LLMResponse = await loop.run_in_executor(
            None, lambda: self._call_llm(transcript)
        )
        record = AnalysisRecord(
            id=uuid.uuid4(),
            summary=llm_response.summary,
            action_items=llm_response.action_items,
        )
        self._storage.save(record)
        return record

    async def analyze_batch(self, transcripts: list[str]) -> list[AnalysisRecord]:
        return await asyncio.gather(*[self.analyze_async(t) for t in transcripts])
