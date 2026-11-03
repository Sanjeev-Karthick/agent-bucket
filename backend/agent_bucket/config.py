from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="AB_", env_file=".env", extra="ignore")

    data_dir: Path = Path(".data")
    ui_dir: Path = Path("frontend/dist")
    source: Literal["demo", "s3"] = "demo"
    demo_dir: Path = Path("examples/demo-data")
    api_token: SecretStr = SecretStr("local-demo-token-change-me")
    embedding_provider: Literal["fastembed", "hash"] = "fastembed"
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dimensions: int = Field(default=384, ge=8, le=4096)
    s3_endpoint: str | None = None
    s3_bucket: str = "agent-bucket-demo"
    s3_prefix: str = ""
    s3_region: str = "us-east-1"
    s3_addressing_style: Literal["path", "virtual", "auto"] = "path"
    chunk_chars: int = Field(default=1600, ge=128, le=16000)
    chunk_overlap: int = Field(default=160, ge=0)
    max_object_bytes: int = Field(default=20 * 1024 * 1024, ge=1)
    max_objects: int = Field(default=10000, ge=1)

    @field_validator("s3_endpoint", mode="before")
    @classmethod
    def empty_endpoint_is_default(cls, value: str | None) -> str | None:
        return value or None

    @model_validator(mode="after")
    def validate_settings(self) -> "Settings":
        if self.chunk_overlap >= self.chunk_chars:
            raise ValueError("chunk_overlap must be less than chunk_chars")
        if len(self.api_token.get_secret_value()) < 16:
            raise ValueError("AB_API_TOKEN must contain at least 16 characters")
        if self.source == "s3" and not self.s3_bucket:
            raise ValueError("AB_S3_BUCKET is required for S3")
        return self
