"""
Task API — a small CRUD API for a to-do list.
Built with FastAPI. Data lives in memory only (resets on restart — that's intentional, see README).
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Task API",
    version="1.0",
    description="A small in-memory CRUD API for managing a to-do list.",
)

# ---------------------------------------------------------------------------
# Stage 2: in-memory "database" — just a list, pre-filled with 3 example tasks
# ---------------------------------------------------------------------------
tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Write README", "done": False},
    {"id": 3, "title": "Learn FastAPI", "done": True},
]
next_id = 4  # tracks the next free id so we never reuse one, even after deletes


# ---------------------------------------------------------------------------
# Request/response models
# ---------------------------------------------------------------------------
class TaskCreate(BaseModel):
    title: Optional[str] = None  # optional here so a missing title is our own 400,
    # not FastAPI's default 422 "unprocessable entity"


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


# ---------------------------------------------------------------------------
# Stage 1: root + health
# ---------------------------------------------------------------------------
@app.get("/", tags=["meta"], summary="API info")
def read_root():
    """Describes the API and lists its endpoints."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks", "/tasks/{id}", "/health", "/stats", "/reset"],
    }


@app.get("/health", tags=["meta"], summary="Health check")
def health_check():
    """Returns ok if the server is alive. Used by monitors/load balancers."""
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Stage 2: Read (list + single), with filtering/search/pagination as extras
# ---------------------------------------------------------------------------
@app.get("/tasks", tags=["tasks"], summary="List tasks")
def list_tasks(
    done: Optional[bool] = None,
    search: Optional[str] = None,
    limit: Optional[int] = None,
    offset: int = 0,
):
    """
    Returns all tasks. Optional query params:
    - done: filter by completion status (true/false)
    - search: only tasks whose title contains this text (case-insensitive)
    - limit / offset: pagination — real APIs never return "everything" at once
    """
    result = tasks

    if done is not None:
        result = [t for t in result if t["done"] == done]

    if search:
        needle = search.lower()
        result = [t for t in result if needle in t["title"].lower()]

    if limit is not None:
        result = result[offset : offset + limit]
    elif offset:
        result = result[offset:]

    return result


@app.get("/tasks/{task_id}", tags=["tasks"], summary="Get a single task")
def get_task(task_id: int):
    """Returns one task by id, or 404 if it doesn't exist."""
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


# ---------------------------------------------------------------------------
# Stage 3: Create
# ---------------------------------------------------------------------------
@app.post("/tasks", status_code=201, tags=["tasks"], summary="Create a task")
def create_task(task: TaskCreate):
    """
    Creates a new task from {"title": "..."}.
    - Assigns the next free id
    - Sets done to false
    - 400 if title is missing or empty
    """
    global next_id

    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="title is required and cannot be empty")

    new_task = {"id": next_id, "title": task.title.strip(), "done": False}
    tasks.append(new_task)
    next_id += 1
    return new_task


# ---------------------------------------------------------------------------
# Stage 4: Update & Delete
# ---------------------------------------------------------------------------
@app.put("/tasks/{task_id}", tags=["tasks"], summary="Update a task")
def update_task(task_id: int, update: TaskUpdate):
    """
    Replaces a task's title and/or done with what's in the request body.
    - 404 if the id doesn't exist
    - 400 if title is provided but empty, or if the body has neither field
    """
    for task in tasks:
        if task["id"] == task_id:
            if update.title is None and update.done is None:
                raise HTTPException(status_code=400, detail="Provide at least title or done")
            if update.title is not None:
                if not update.title.strip():
                    raise HTTPException(status_code=400, detail="title cannot be empty")
                task["title"] = update.title.strip()
            if update.done is not None:
                task["done"] = update.done
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@app.delete("/tasks/{task_id}", status_code=204, tags=["tasks"], summary="Delete a task")
def delete_task(task_id: int):
    """Removes a task by id. 204 with no body on success, 404 if it doesn't exist."""
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            tasks.pop(i)
            return
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


# ---------------------------------------------------------------------------
# Extras: stats + reset
# ---------------------------------------------------------------------------
@app.get("/stats", tags=["extras"], summary="Task statistics")
def get_stats():
    """The server computing something instead of just storing it."""
    total = len(tasks)
    done_count = sum(1 for t in tasks if t["done"])
    return {"total": total, "done": done_count, "open": total - done_count}


@app.post("/reset", tags=["extras"], summary="Reset to the 3 example tasks")
def reset_tasks():
    """Restores the original 3 example tasks. Handy for demos."""
    global tasks, next_id
    tasks = [
        {"id": 1, "title": "Buy milk", "done": False},
        {"id": 2, "title": "Write README", "done": False},
        {"id": 3, "title": "Learn FastAPI", "done": True},
    ]
    next_id = 4
    return {"status": "reset", "tasks": tasks}