from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import uuid4

from app.models.device import Device


class DeviceRepository:
    def __init__(self) -> None:
        self._devices: dict[str, Device] = {}

    async def create(self, ip_address: str, username: str, port: int) -> Device:
        device_id = str(uuid4())
        device = Device(
            id=device_id,
            ip_address=ip_address,
            username=username,
            port=port,
            created_at=datetime.now(),
        )
        self._devices[device_id] = device
        return device

    async def get_by_id(self, device_id: str) -> Optional[Device]:
        return self._devices.get(device_id)

    async def get_all(self) -> list[Device]:
        return list(self._devices.values())

    async def update_data(self, device_id: str, data: dict) -> Optional[Device]:
        device = self._devices.get(device_id)
        if device:
            device.data = data
            device.last_accessed = datetime.now()
        return device

    async def delete(self, device_id: str) -> bool:
        if device_id in self._devices:
            del self._devices[device_id]
            return True
        return False

