# library-agent

## Start the service
```powershell
uv run uvicorn app.main:create_app --factory --reload
```

## Review code quality
Comprehensive code quality
```powershell
uv run ruff check app --fix
uv run ruff format app
uv run mypy app
```

## Verify the local API
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Doc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- Process status: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
