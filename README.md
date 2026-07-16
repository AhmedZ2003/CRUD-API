# Task API

A small in-memory CRUD API for managing a to-do list, built with FastAPI.

## What this is

A REST API with five endpoints for creating, reading, updating, and deleting tasks. Data lives only in memory (a Python list).It resets whenever the server restarts.

## How to run it

```bash
pip install -r requirements.txt
python -m uvicorn app:app --reload
```

The server starts on `http://localhost:8000`. Interactive docs (Swagger UI) are at `http://localhost:8000/docs`.

## Endpoints

| Method | Path           | Description                          | Success | Errors        |
|--------|----------------|---------------------------------------|---------|---------------|
| GET    | `/`            | API info                              | 200     | —             |
| GET    | `/health`      | Health check                          | 200     | —             |
| GET    | `/tasks`       | List all tasks                        | 200     | —             |
| GET    | `/tasks/{id}`  | Get one task                          | 200     | 404           |
| POST   | `/tasks`       | Create a task (`{"title": "..."}`)    | 201     | 400           |
| PUT    | `/tasks/{id}`  | Update a task's title and/or done     | 200     | 400, 404      |
| DELETE | `/tasks/{id}`  | Delete a task                         | 204     | 404           |

## Example

```bash
curl.exe -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
```

```
HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## NOTE: If curl doesn't work, use Invoke-RestMethod
## Example
```bash
Invoke-RestMethod -Uri "http://localhost:8000/tasks" -Method Post -ContentType "application/json" -Body '{"title":"Buy milk"}' 
```
