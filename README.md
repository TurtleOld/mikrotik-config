# Mikrotik Config Web Interface

Web interface for managing Mikrotik devices via REST API.

## Features

- Add and display Mikrotik device data
- REST API integration with Mikrotik devices
- Modern web interface with Alpine.js and HTMX
- Docker support with docker-compose

## Requirements

- Python 3.12+
- Docker and Docker Compose

## Installation

### Local Development

```bash
uv pip install -e .
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Альтернативный способ через Litestar CLI (может иметь проблемы с анализом типов):
```bash
uv run litestar run --reload --app app.main:app
```

### Docker

```bash
docker-compose up --build
```

### GitHub Container Registry

Образ автоматически собирается и публикуется в GitHub Container Registry при каждом push в main ветку.

Использование образа из registry:

```bash
docker pull ghcr.io/turtleold/mikrotik-config:latest
docker run -p 8000:8000 ghcr.io/turtleold/mikrotik-config:latest
```

Или с docker-compose:

```yaml
services:
  web:
    image: ghcr.io/turtleold/mikrotik-config:latest
    ports:
      - '8000:8000'
```

## Usage

1. Open http://localhost:8000
2. Enter Mikrotik device IP address
3. View and manage device data

## Configuration

Set environment variables:
- `APP_ENV`: Application environment (development/production)

## GitHub Actions

Проект включает GitHub Actions workflow для автоматической сборки Docker образа и публикации в GitHub Container Registry (ghcr.io).

Workflow запускается автоматически при:
- Push в ветку `main`
- Создании тега версии (например, `v1.0.0`)
- Pull Request в ветку `main`

Образы доступны по адресу: `ghcr.io/turtleold/mikrotik-config`
