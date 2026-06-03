"""Schemas for bulk question import workflows."""

from datetime import datetime
from typing import Any, Optional
import uuid

from pydantic import BaseModel, ConfigDict, Field


class ImportQuestionsResponse(BaseModel):
    """Initial async import response."""

    job_id: uuid.UUID
    status: str


class ImportJobStatusResponse(BaseModel):
    """Detailed import job response including preview and failures."""

    id: uuid.UUID
    file_type: str
    original_filename: str
    status: str
    total_rows: Optional[int] = None
    imported_count: int = 0
    failed_rows: list[dict[str, Any]] = Field(default_factory=list)
    parsed_preview: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ImportConfirmRequest(BaseModel):
    """Faculty selected rows to persist from preview."""

    approved_indices: list[int] = Field(default_factory=list)


class ImportConfirmResponse(BaseModel):
    """Result of persisting approved rows."""

    imported_count: int
    failed_rows: list[dict[str, Any]] = Field(default_factory=list)


class ImportHistoryResponse(BaseModel):
    """History list response item for faculty imports."""

    id: uuid.UUID
    file_type: str
    original_filename: str
    status: str
    total_rows: Optional[int] = None
    imported_count: int = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
