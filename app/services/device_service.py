from __future__ import annotations

from typing import Optional

import structlog

from app.config import settings
from app.models.device import DeviceCreate, DeviceResponse
from app.repositories.device_repository import DeviceRepository
from app.services.mikrotik_service import MikrotikService

logger = structlog.get_logger(__name__)


class DeviceService:
    def __init__(self, repository: DeviceRepository) -> None:
        self._repository = repository

    async def create_device(self, device_data: DeviceCreate) -> DeviceResponse:
        username = device_data.username or settings.mikrotik_username
        logger.info(
            "Creating new device",
            ip_address=device_data.ip_address,
            port=device_data.port,
        )

        device = None
        try:
            logger.info(
                "Fetching data from Mikrotik device before creating",
                ip_address=device_data.ip_address,
            )

            async with MikrotikService() as mikrotik:
                mikrotik_data = await mikrotik.get_all_data(
                    ip_address=device_data.ip_address,
                    username=device_data.username if device_data.username else None,
                    password=device_data.password if device_data.password else None,
                    port=device_data.port,
                )

            logger.info(
                "Successfully connected to Mikrotik device, creating device in repository",
                ip_address=device_data.ip_address,
                has_system_info="system" in mikrotik_data and bool(mikrotik_data["system"]),
                interfaces_count=len(mikrotik_data.get("interfaces", [])),
            )

            device = await self._repository.create(
                ip_address=device_data.ip_address,
                username=username,
                port=device_data.port,
            )
            logger.info(
                "Device created in repository",
                device_id=device.id,
                ip_address=device.ip_address,
            )

            await self._repository.update_data(device.id, mikrotik_data)

            updated_device = await self._repository.get_by_id(device.id)
            if not updated_device:
                logger.error(
                    "Failed to retrieve created device",
                    device_id=device.id,
                )
                raise RuntimeError("Failed to retrieve created device")

            logger.info(
                "Device successfully created and configured",
                device_id=updated_device.id,
                ip_address=updated_device.ip_address,
            )

            return DeviceResponse(
                id=updated_device.id,
                ip_address=updated_device.ip_address,
                port=updated_device.port,
                created_at=updated_device.created_at,
                last_accessed=updated_device.last_accessed,
                data=updated_device.data,
            )
        except Exception as e:
            if device:
                logger.warning(
                    "Removing device from repository due to error",
                    device_id=device.id,
                    ip_address=device_data.ip_address,
                )
                await self._repository.delete(device.id)

            logger.error(
                "Failed to create device",
                ip_address=device_data.ip_address,
                port=device_data.port,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise

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
        username: Optional[str] = None,
        password: Optional[str] = None,
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
