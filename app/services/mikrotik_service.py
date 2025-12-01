from __future__ import annotations

import base64
from typing import Any, Optional

import httpx

from app.config import settings


class MikrotikService:
    def __init__(self) -> None:
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> 'MikrotikService':
        self._client = httpx.AsyncClient(timeout=settings.mikrotik_timeout)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_auth_header(self, username: str, password: str) -> str:
        credentials = f'{username}:{password}'
        encoded = base64.b64encode(credentials.encode()).decode()
        return f'Basic {encoded}'

    async def get_system_info(
        self,
        ip_address: str,
        username: str,
        password: str,
        port: int = 80,
    ) -> dict[str, Any]:
        if not self._client:
            raise RuntimeError('Service not initialized. Use async context manager.')

        url = f'http://{ip_address}:{port}/rest/system/resource'
        headers = {
            'Authorization': self._get_auth_header(username, password),
            'Content-Type': 'application/json',
        }

        try:
            response = await self._client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0] if isinstance(data[0], dict) else {}
            return {}
        except httpx.HTTPStatusError as e:
            raise ConnectionError(f'Mikrotik API error: {e.response.status_code}') from e
        except httpx.RequestError as e:
            raise ConnectionError(f'Failed to connect to Mikrotik device: {str(e)}') from e

    async def get_interfaces(
        self,
        ip_address: str,
        username: str,
        password: str,
        port: int = 80,
    ) -> list[dict[str, Any]]:
        if not self._client:
            raise RuntimeError('Service not initialized. Use async context manager.')

        url = f'http://{ip_address}:{port}/rest/interface'
        headers = {
            'Authorization': self._get_auth_header(username, password),
            'Content-Type': 'application/json',
        }

        try:
            response = await self._client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data if isinstance(data, list) else []
        except httpx.HTTPStatusError as e:
            raise ConnectionError(f'Mikrotik API error: {e.response.status_code}') from e
        except httpx.RequestError as e:
            raise ConnectionError(f'Failed to connect to Mikrotik device: {str(e)}') from e

    async def get_all_data(
        self,
        ip_address: str,
        username: str,
        password: str,
        port: int = 80,
    ) -> dict[str, Any]:
        system_info = await self.get_system_info(ip_address, username, password, port)
        interfaces = await self.get_interfaces(ip_address, username, password, port)

        return {
            'system': system_info,
            'interfaces': interfaces,
        }

