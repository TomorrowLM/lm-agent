"""应用配置 —— 统一加载 .env，提供类型安全的配置项"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 应用
    app_name: str = "LM Agent API"
    app_version: str = "0.1.0"
    debug: bool = False

    # 服务
    host: str = "127.0.0.1"
    port: int = 3000

    # LLM
    ai_base_url: str = "https://api.openai.com/v1"
    openai_base_url: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_api_key: str = ""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
