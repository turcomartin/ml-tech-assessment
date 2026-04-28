from pathlib import Path

import pydantic_settings

_REPO_ROOT = Path(__file__).resolve().parent.parent


class EnvConfigs(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(
        env_file=str(_REPO_ROOT / ".env"), env_file_encoding="utf-8"
    )

    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-2024-08-06"
    MOCK_LLM: bool = False
