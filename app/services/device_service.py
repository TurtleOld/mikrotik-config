from __future__ import annotations

from typing import Optional

from app.models.device import Device, DeviceCreate, DeviceResponse
from app.repositories.device_repository import DeviceRepository
from app.services.mikrotik_service import MikrotikService


class DeviceService:
    def __init__(self, repository: DeviceRepository) -> None:
        self._repository = repository

    async def create_device(self, device_data: DeviceCreate) -> DeviceResponse:
        device = await self._repository.create(
            ip_address=device_data.ip_address,
            username=device_data.username,
            port=device_data.port,
        )

        async with MikrotikService() as mikrotik:
            mikrotik_data = await mikrotik.get_all_data(
                ip_address=device_data.ip_address,
                username=device_data.username,
                password=device_data.password,
                port=device_data.port,
            )

        await self._repository.update_data(device.id, mikrotik_data)

        updated_device = await self._repository.get_by_id(device.id)
        if not updated_device:
            raise RuntimeError('Failed to retrieve created device')

        return DeviceResponse(
            id=updated_device.id,
            ip_address=updated_device.ip_address,
            port=updated_device.port,
            created_at=updated_device.created_at,
            last_accessed=updated_device.last_accessed,
            data=updated_device.data,
        )

    async def get_device(self, device_id: str) -> Optional[DeviceResponse]:
        device = await self._repository.get_by_id(device_id)
        if not device:
            return None

        return DeviceResponse(
            id=device.id,
            ip_address=device.ip_address,
            port=device.port,
            created_at=device.created_at,
            last_accessed=device.last_accessed,
            data=device.data,
        )

    async def get_all_devices(self) -> list[DeviceResponse]:
        devices = await self._repository.get_all()
        return [
            DeviceResponse(
                id=device.id,
                ip_address=device.ip_address,
                port=device.port,
                created_at=device.created_at,
                last_accessed=device.last_accessed,
                data=device.data,
            )
            for device in devices
        ]

    async def refresh_device_data(
        self,
        device_id: str,
        username: str,
        password: str,
    ) -> Optional[DeviceResponse]:
        device = await self._repository.get_by_id(device_id)
        if not device:
            return None

        async with MikrotikService() as mikrotik:
            mikrotik_data = await mikrotik.get_all_data(
                ip_address=device.ip_address,
                username=username,
                password=password,
                port=device.port,
            )

        await self._repository.update_data(device_id, mikrotik_data)

        updated_device = await self._repository.get_by_id(device_id)
        if not updated_device:
            return None

        return DeviceResponse(
            id=updated_device.id,
            ip_address=updated_device.ip_address,
            port=updated_device.port,
            created_at=updated_device.created_at,
            last_accessed=updated_device.last_accessed,
            data=updated_device.data,
        )

    async def delete_device(self, device_id: str) -> bool:
        return await self._repository.delete(device_id)

