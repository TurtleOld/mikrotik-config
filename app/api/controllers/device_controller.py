from __future__ import annotations

from typing import Annotated

import structlog
from litestar import Controller, Request, get, post, delete
from litestar.response import Template
from litestar.di import Provide
from litestar.params import Dependency

from app.models.device import DeviceCreate, DeviceResponse
from app.repositories.device_repository import DeviceRepository
from app.services.device_service import DeviceService

logger = structlog.get_logger(__name__)


def get_device_service() -> DeviceService:
    repository = DeviceRepository()
    return DeviceService(repository)


class DeviceController(Controller):
    path = '/'
    dependencies = {
        'service': Provide(get_device_service, sync_to_thread=False),
    }

    @get('/', tags=['web'])
    async def index(
        self,
        service: Annotated[DeviceService, Dependency(skip_validation=True)],
    ) -> Template:
        devices = await service.get_all_devices()
        return Template(
            template_name='index.html',
            context={'devices': devices},
        )

    @post('/devices', tags=['devices'])
    async def create_device(
        self,
        request: Request,
        service: Annotated[DeviceService, Dependency(skip_validation=True)],
    ) -> Template:
        form_data = await request.form()
        ip_address = form_data.get('ip_address', '').strip()
        username_str = form_data.get('username', '').strip()
        password_str = form_data.get('password', '').strip()
        port_str = form_data.get('port', '80').strip()
        
        username = username_str if username_str else None
        password = password_str if password_str else None
        port = int(port_str) if port_str else 80

        data = DeviceCreate(
            ip_address=ip_address,
            username=username,
            password=password,
            port=port,
        )

        logger.info(
            'Received request to create device',
            ip_address=data.ip_address,
            port=data.port,
            username=data.username,
        )

        try:
            device = await service.create_device(data)
            logger.info(
                'Device created successfully',
                device_id=device.id,
                ip_address=device.ip_address,
            )
            devices = await service.get_all_devices()
            return Template(
                template_name='device_list.html',
                context={'devices': devices, 'message': 'Устройство успешно добавлено'},
            )
        except Exception as e:
            logger.error(
                'Failed to create device in controller',
                ip_address=data.ip_address,
                port=data.port,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            devices = await service.get_all_devices()
            error_message = str(e)
            return Template(
                template_name='device_list.html',
                context={'devices': devices, 'error': error_message},
            )

    @get('/devices', tags=['devices'])
    async def list_devices(
        self,
        service: Annotated[DeviceService, Dependency(skip_validation=True)],
    ) -> Template:
        devices = await service.get_all_devices()
        return Template(
            template_name='device_list.html',
            context={'devices': devices},
        )

    @get('/devices/{device_id:str}', tags=['devices'])
    async def get_device(
        self,
        device_id: str,
        service: Annotated[DeviceService, Dependency(skip_validation=True)],
    ) -> Template:
        device = await service.get_device(device_id)
        if not device:
            return Template(
                template_name='device_detail.html',
                context={'error': 'Устройство не найдено'},
            )
        return Template(
            template_name='device_detail.html',
            context={'device': device},
        )

    @delete('/devices/{device_id:str}', tags=['devices'], status_code=200)
    async def delete_device(
        self,
        device_id: str,
        service: Annotated[DeviceService, Dependency(skip_validation=True)],
    ) -> Template:
        await service.delete_device(device_id)
        devices = await service.get_all_devices()
        return Template(
            template_name='device_list.html',
            context={'devices': devices, 'message': 'Устройство успешно удалено'},
        )

