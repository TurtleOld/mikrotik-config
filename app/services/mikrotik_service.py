from __future__ import annotations

import base64
from typing import Any, Optional

import httpx
import structlog

from app.config import settings

logger = structlog.get_logger(__name__)


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

    async def _fetch_endpoint(
        self,
        ip_address: str,
        endpoint: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        port: int = 80,
    ) -> Any:
        if not self._client:
            logger.error('MikrotikService not initialized', service='mikrotik')
            raise RuntimeError('Service not initialized. Use async context manager.')

        auth_username = username or settings.mikrotik_username
        auth_password = password or settings.mikrotik_password

        url = f'http://{ip_address}:{port}/rest/{endpoint}'
        headers = {
            'Authorization': self._get_auth_header(auth_username, auth_password),
            'Content-Type': 'application/json',
        }

        try:
            response = await self._client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0] if isinstance(data[0], dict) else data
            return data if isinstance(data, dict) else {}
        except httpx.HTTPStatusError as e:
            logger.warning(
                'Mikrotik API HTTP error',
                ip_address=ip_address,
                endpoint=endpoint,
                status_code=e.response.status_code,
            )
            return {}
        except httpx.RequestError as e:
            logger.warning(
                'Failed to fetch endpoint',
                ip_address=ip_address,
                endpoint=endpoint,
                error=str(e),
            )
            return {}
        except Exception as e:
            logger.warning(
                'Unexpected error while fetching endpoint',
                ip_address=ip_address,
                endpoint=endpoint,
                error=str(e),
            )
            return {}

    async def get_system_info(
        self,
        ip_address: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        port: int = 80,
    ) -> dict[str, Any]:
        if not self._client:
            logger.error('MikrotikService not initialized', service='mikrotik')
            raise RuntimeError('Service not initialized. Use async context manager.')

        auth_username = username or settings.mikrotik_username
        auth_password = password or settings.mikrotik_password

        url = f'http://{ip_address}:{port}/rest/system/resource'
        headers = {
            'Authorization': self._get_auth_header(auth_username, auth_password),
            'Content-Type': 'application/json',
        }

        logger.info(
            'Fetching system info from Mikrotik',
            ip_address=ip_address,
            port=port,
            url=url,
        )

        try:
            response = await self._client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.info(
                'Successfully fetched system info',
                ip_address=ip_address,
                status_code=response.status_code,
                data_length=len(data) if isinstance(data, list) else 0,
            )
            if isinstance(data, list) and len(data) > 0:
                return data[0] if isinstance(data[0], dict) else {}
            return {}
        except httpx.HTTPStatusError as e:
            logger.error(
                'Mikrotik API HTTP error',
                ip_address=ip_address,
                port=port,
                status_code=e.response.status_code,
                response_text=e.response.text[:200] if e.response.text else None,
                exc_info=True,
            )
            raise ConnectionError(f'Mikrotik API error: {e.response.status_code}') from e
        except httpx.RequestError as e:
            logger.error(
                'Failed to connect to Mikrotik device',
                ip_address=ip_address,
                port=port,
                error=str(e),
                exc_info=True,
            )
            raise ConnectionError(f'Failed to connect to Mikrotik device: {str(e)}') from e
        except Exception as e:
            logger.error(
                'Unexpected error while fetching system info',
                ip_address=ip_address,
                port=port,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise

    async def get_interfaces(
        self,
        ip_address: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        port: int = 80,
    ) -> list[dict[str, Any]]:
        if not self._client:
            logger.error('MikrotikService not initialized', service='mikrotik')
            raise RuntimeError('Service not initialized. Use async context manager.')

        auth_username = username or settings.mikrotik_username
        auth_password = password or settings.mikrotik_password

        url = f'http://{ip_address}:{port}/rest/interface'
        headers = {
            'Authorization': self._get_auth_header(auth_username, auth_password),
            'Content-Type': 'application/json',
        }

        logger.info(
            'Fetching interfaces from Mikrotik',
            ip_address=ip_address,
            port=port,
            url=url,
        )

        try:
            response = await self._client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.info(
                'Successfully fetched interfaces',
                ip_address=ip_address,
                status_code=response.status_code,
                interfaces_count=len(data) if isinstance(data, list) else 0,
            )
            return data if isinstance(data, list) else []
        except httpx.HTTPStatusError as e:
            logger.error(
                'Mikrotik API HTTP error while fetching interfaces',
                ip_address=ip_address,
                port=port,
                status_code=e.response.status_code,
                response_text=e.response.text[:200] if e.response.text else None,
                exc_info=True,
            )
            raise ConnectionError(f'Mikrotik API error: {e.response.status_code}') from e
        except httpx.RequestError as e:
            logger.error(
                'Failed to connect to Mikrotik device for interfaces',
                ip_address=ip_address,
                port=port,
                error=str(e),
                exc_info=True,
            )
            raise ConnectionError(f'Failed to connect to Mikrotik device: {str(e)}') from e
        except Exception as e:
            logger.error(
                'Unexpected error while fetching interfaces',
                ip_address=ip_address,
                port=port,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise

    async def get_identity(
        self,
        ip_address: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        port: int = 80,
    ) -> dict[str, Any]:
        return await self._fetch_endpoint(ip_address, 'system/identity', username, password, port)

    async def get_routerboard(
        self,
        ip_address: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        port: int = 80,
    ) -> dict[str, Any]:
        return await self._fetch_endpoint(ip_address, 'system/routerboard', username, password, port)

    async def get_clock(
        self,
        ip_address: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        port: int = 80,
    ) -> dict[str, Any]:
        return await self._fetch_endpoint(ip_address, 'system/clock', username, password, port)

    async def get_license(
        self,
        ip_address: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        port: int = 80,
    ) -> dict[str, Any]:
        return await self._fetch_endpoint(ip_address, 'system/license', username, password, port)

    async def get_all_data(
        self,
        ip_address: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        port: int = 80,
    ) -> dict[str, Any]:
        logger.info(
            'Fetching all data from Mikrotik',
            ip_address=ip_address,
            port=port,
        )
        try:
            system_info = await self.get_system_info(ip_address, username, password, port)
            interfaces = await self.get_interfaces(ip_address, username, password, port)
            identity = await self.get_identity(ip_address, username, password, port)
            routerboard = await self.get_routerboard(ip_address, username, password, port)
            clock = await self.get_clock(ip_address, username, password, port)
            license_info = await self.get_license(ip_address, username, password, port)

            logger.info(
                'Successfully fetched all data from Mikrotik',
                ip_address=ip_address,
                port=port,
                has_system_info=bool(system_info),
                interfaces_count=len(interfaces),
                has_identity=bool(identity),
                has_routerboard=bool(routerboard),
            )

            return {
                'system': system_info,
                'interfaces': interfaces,
                'identity': identity,
                'routerboard': routerboard,
                'clock': clock,
                'license': license_info,
            }
        except Exception as e:
            logger.error(
                'Failed to fetch all data from Mikrotik',
                ip_address=ip_address,
                port=port,
                error=str(e),
                error_type=type(e).__name__,
                exc_info=True,
            )
            raise

