from __future__ import annotations

from typing import Annotated

from litestar import Controller, get, post, delete
from litestar.response import Template
from litestar.di import Provide
from litestar.params import Dependency

from app.models.device import DeviceCreate, DeviceResponse
from app.repositories.device_repository import DeviceRepository
from app.services.device_service import DeviceService


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
        data: DeviceCreate,
        service: Annotated[DeviceService, Dependency(skip_validation=True)],
    ) -> Template:
        try:
            device = await service.create_device(data)
            devices = await service.get_all_devices()
            return Template(
                template_name='device_list.html',
                context={'devices': devices, 'message': 'Устройство успешно добавлено'},
            )
        except Exception as e:
            devices = await service.get_all_devices()
            return Template(
                template_name='device_list.html',
                context={'devices': devices, 'error': str(e)},
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

