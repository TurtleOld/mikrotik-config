from __future__ import annotations

from litestar import Litestar
from litestar.config.compression import CompressionConfig
from litestar.config.cors import CORSConfig
from litestar.static_files import create_static_files_router
from litestar.template import TemplateConfig
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.contrib.jinja import JinjaTemplateEngine

from app.api.controllers import device_controller, health_controller
from app.config import settings


template_config = TemplateConfig(
    directory='app/templates',
    engine=JinjaTemplateEngine,
)

cors_config = CORSConfig(
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

compression_config = CompressionConfig(backend='gzip')

rate_limit_config = RateLimitConfig(
    rate_limit='100/minute',
    exclude_opt_key='skip_rate_limit',
)

app = Litestar(
    route_handlers=[
        device_controller.DeviceController,
        health_controller.HealthController,
        health_controller.FaviconController,
        create_static_files_router(
            path='/static',
            directories=['app/static'],
        ),
    ],
    template_config=template_config,
    cors_config=cors_config,
    compression_config=compression_config,
    debug=settings.app_env == 'development',
)

