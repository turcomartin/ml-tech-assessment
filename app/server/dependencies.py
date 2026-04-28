from functools import lru_cache

from app import ports
from app.configurations import EnvConfigs
from app.server.service import AnalysisService
from app.server.storage import InMemoryStorage


@lru_cache(maxsize=1)
def get_configs() -> EnvConfigs:
    return EnvConfigs()


@lru_cache(maxsize=1)
def get_storage() -> InMemoryStorage:
    return InMemoryStorage()


@lru_cache(maxsize=1)
def get_llm_adapter() -> ports.LLm:
    configs = get_configs()
    if configs.MOCK_LLM:
        from app.adapters.mock import MockLLmAdapter

        return MockLLmAdapter()
    from app.adapters.openai import OpenAIAdapter

    return OpenAIAdapter(api_key=configs.OPENAI_API_KEY, model=configs.OPENAI_MODEL)


def get_analysis_service() -> AnalysisService:
    return AnalysisService(llm=get_llm_adapter(), storage=get_storage())
