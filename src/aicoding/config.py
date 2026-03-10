from __future__ import annotations

from functools import lru_cache
import logging
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from aicoding.models.base import AICodingModel


class DatabaseSettings(AICodingModel):
    url: str
    pool_size: int
    max_overflow: int
    pool_timeout: int
    echo: bool


class DaemonSettings(AICodingModel):
    app_name: str
    host: str
    port: int

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


class SessionSettings(AICodingModel):
    backend: Literal["fake", "tmux"]
    poll_interval_seconds: float
    idle_threshold_seconds: float
    max_nudge_count: int


class AuthSettings(AICodingModel):
    token: str
    token_file: Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="AICODING_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = "development"
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/aicoding"
    database_pool_size: int = Field(default=5, gt=0)
    database_max_overflow: int = Field(default=10, ge=0)
    database_pool_timeout: int = Field(default=30, gt=0)
    database_echo: bool = False
    log_level: str = "INFO"
    daemon_app_name: str = "AI Coding Orchestrator"
    daemon_host: str = "127.0.0.1"
    daemon_port: int = Field(default=8000, ge=1, le=65535)
    session_backend: Literal["fake", "tmux"] = "fake"
    session_poll_interval_seconds: float = Field(default=1.0, gt=0)
    session_idle_threshold_seconds: float = Field(default=30.0, gt=0)
    session_max_nudge_count: int = Field(default=2, ge=1)
    auth_token: str = "change-me"
    auth_token_file: Path = Field(default=Path(".runtime/daemon.token"))

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("database_url must not be blank")
        if "://" not in stripped:
            raise ValueError("database_url must be a URL-like SQLAlchemy connection string")
        return stripped

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        normalized = value.strip().upper()
        if normalized not in logging.getLevelNamesMapping():
            raise ValueError(f"Unsupported log level: {value}")
        return normalized

    @field_validator("env", "daemon_app_name", "daemon_host")
    @classmethod
    def validate_non_blank_strings(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("value must not be blank")
        return stripped

    @property
    def normalized_log_level(self) -> str:
        return self.log_level.upper()

    @property
    def database(self) -> DatabaseSettings:
        return DatabaseSettings(
            url=self.database_url,
            pool_size=self.database_pool_size,
            max_overflow=self.database_max_overflow,
            pool_timeout=self.database_pool_timeout,
            echo=self.database_echo,
        )

    @property
    def daemon(self) -> DaemonSettings:
        return DaemonSettings(
            app_name=self.daemon_app_name,
            host=self.daemon_host,
            port=self.daemon_port,
        )

    @property
    def session(self) -> SessionSettings:
        return SessionSettings(
            backend=self.session_backend,
            poll_interval_seconds=self.session_poll_interval_seconds,
            idle_threshold_seconds=self.session_idle_threshold_seconds,
            max_nudge_count=self.session_max_nudge_count,
        )

    @property
    def auth(self) -> AuthSettings:
        return AuthSettings(
            token=self.auth_token,
            token_file=self.auth_token_file,
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
