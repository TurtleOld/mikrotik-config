from __future__ import annotations

from litestar import Controller, get
from litestar.response import Response


class HealthController(Controller):
    path = '/health'
    
    @get('/', tags=['health'], include_in_schema=True)
    async def health_check(self) -> Response:
        return Response(content={'status': 'ok'}, status_code=200)


class FaviconController(Controller):
    path = '/favicon.ico'
    
    @get('/', tags=['static'], include_in_schema=False)
    async def favicon(self) -> Response:
        return Response(content=None, status_code=204)

