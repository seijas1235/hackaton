from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal, Optional

from pydantic import BaseModel, Field, ConfigDict


class Settings(BaseModel):
    model_config = ConfigDict(extra="ignore")
    env: Literal["local", "dev", "staging", "prod"] = Field(
        default="local", description="Environment name"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )

    aws_region: Optional[str] = None
    aws_profile: Optional[str] = None
    
    table_name: str = "finance"

    jwt_secret: Optional[str] = None
    jwt_algorithm: str = "HS256"
    
    agent_id: Optional[str] = None
    agent_alias_id: Optional[str] = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load settings from environment variables with sensible defaults."""
    return Settings(
        env=os.getenv("ENV", "local"),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        aws_region=os.getenv("AWS_REGION") or None,
        aws_profile=os.getenv("AWS_PROFILE") or None,
        table_name=os.getenv("TABLE_NAME", "finance"),
        jwt_secret=os.getenv("JWT_SECRET") or None,
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        agent_id=os.getenv("AGENT_ID") or None,
        agent_alias_id=os.getenv("AGENT_ALIAS_ID") or None,
    )
