import random

import pydantic
from app import ports


class MockLLmAdapter(ports.LLm):
    def run_completion(
        self, system_prompt: str, user_prompt: str, dto: type[pydantic.BaseModel]
    ) -> pydantic.BaseModel:
        uid = random.randint(10000, 99999)
        return dto(
            summary="Mock summary of the transcript.",
            action_items=[f"Mock action 1 #{uid}", f"Mock action 2 #{uid}"],
        )
