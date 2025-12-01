from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class DeviceCreate(BaseModel):
    ip_address: str = Field(..., description='IP address of Mikrotik device')
    username: str = Field(default='admin', description='Username for authentication')
    password: str = Field(..., description='Password for authentication')
    port: int = Field(default=80, ge=1, le=65535, description='Port number')

    @field_validator('ip_address')
    @classmethod
    def validate_ip_address(cls, v: str) -> str:
        parts = v.split('.')
        if len(parts) != 4:
            raise ValueError('Invalid IP address format')
        for part in parts:
            if not part.isdigit() or not 0 <= int(part) <= 255:
                raise ValueError('Invalid IP address format')
        return v


class Device(BaseModel):
    id: str
    ip_address: str
    username: str
    port: int
    created_at: datetime
    last_accessed: Optional[datetime] = None
    data: Optional[dict[str, Any]] = None


class DeviceResponse(BaseModel):
    id: str
    ip_address: str
    port: int
    created_at: datetime
    last_accessed: Optional[datetime]
    data: Optional[dict[str, Any]] = None

