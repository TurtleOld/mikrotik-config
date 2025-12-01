from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

from app.models.device import Device

DEVICES_FILE = Path('devices.yaml')


class DeviceRepository:
    def __init__(self, devices_file: Path = DEVICES_FILE) -> None:
        self._devices_file = devices_file
        self._lock = asyncio.Lock()

    def _load_devices(self) -> dict[str, dict]:
        if not self._devices_file.exists():
            return {}
        with open(self._devices_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
            return data.get('devices', {})

    def _save_devices(self, devices: dict[str, dict]) -> None:
        self._devices_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._devices_file, 'w', encoding='utf-8') as f:
            yaml.dump({'devices': devices}, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

    def _device_to_dict(self, device: Device) -> dict:
        return {
            'id': device.id,
            'ip_address': device.ip_address,
            'username': device.username,
            'port': device.port,
            'created_at': device.created_at.isoformat(),
            'last_accessed': device.last_accessed.isoformat() if device.last_accessed else None,
            'data': device.data,
        }

    def _dict_to_device(self, data: dict) -> Device:
        return Device(
            id=data['id'],
            ip_address=data['ip_address'],
            username=data['username'],
            port=data['port'],
            created_at=datetime.fromisoformat(data['created_at']),
            last_accessed=datetime.fromisoformat(data['last_accessed']) if data.get('last_accessed') else None,
            data=data.get('data'),
        )

    async def create(self, ip_address: str, username: str, port: int) -> Device:
        from uuid import uuid4

        async with self._lock:
            devices_dict = self._load_devices()
            device_id = str(uuid4())
            device = Device(
                id=device_id,
                ip_address=ip_address,
                username=username,
                port=port,
                created_at=datetime.now(),
            )
            devices_dict[device_id] = self._device_to_dict(device)
            self._save_devices(devices_dict)
            return device

    async def get_by_id(self, device_id: str) -> Optional[Device]:
        async with self._lock:
            devices_dict = self._load_devices()
            device_data = devices_dict.get(device_id)
            if not device_data:
                return None
            return self._dict_to_device(device_data)

    async def get_all(self) -> list[Device]:
        async with self._lock:
            devices_dict = self._load_devices()
            return [self._dict_to_device(data) for data in devices_dict.values()]

    async def update_data(self, device_id: str, data: dict) -> Optional[Device]:
        async with self._lock:
            devices_dict = self._load_devices()
            device_data = devices_dict.get(device_id)
            if not device_data:
                return None
            device_data['data'] = data
            device_data['last_accessed'] = datetime.now().isoformat()
            devices_dict[device_id] = device_data
            self._save_devices(devices_dict)
            return self._dict_to_device(device_data)

    async def delete(self, device_id: str) -> bool:
        async with self._lock:
            devices_dict = self._load_devices()
            if device_id not in devices_dict:
                return False
            del devices_dict[device_id]
            self._save_devices(devices_dict)
            return True
