import secrets
from functools import lru_cache

import fastapi
import fastapi.security

from app import ports
from app.configurations import EnvConfigs
from app.server.service import AnalysisService
from app.server.storage import InMemoryStorage

_basic_auth = fastapi.security.HTTPBasic()


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


def verify_credentials(
    credentials: fastapi.security.HTTPBasicCredentials = fastapi.Depends(_basic_auth),
) -> None:
    configs = get_configs()
    valid_username = secrets.compare_digest(credentials.username, configs.API_USERNAME)
    valid_password = secrets.compare_digest(credentials.password, configs.API_PASSWORD)
    if not (valid_username and valid_password):
        raise fastapi.HTTPException(status_code=401, detail="Invalid credentials")


def get_analysis_service() -> AnalysisService:
    return AnalysisService(llm=get_llm_adapter(), storage=get_storage())
