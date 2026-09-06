from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

from repositories import PostgresTaskRepository, TaskCreate, TaskUpdate

from dotenv import load_dotenv
import os

load_dotenv()

CONNECTION_STRING = os.getenv(
    "POSTGRES_URL", "postgresql://postgres:postgres@db:5432/tasks"
)

repository = PostgresTaskRepository(CONNECTION_STRING)


app = FastAPI(title="task api", version="1.0.0")


@app.get("/")
def root():
    return {
        "name": "task api",
        "version": "1.0.0",
        "endpoints": {
            "list_tasks": "Get /tasks",
            "get_tasks": "Get /tasks/{id}",
            "create_task": "Post /tasks",
            "update_task": "Put /tasks/{id}",
            "delete_task": "Delete /tasks/{id}",
        },
    }


@app.get("/tasks", summary="List all tasks from database")
def get_tasks_db():
    return repository.list_tasks()


@app.get("/tasks/{task_id}", summary="Get one task by ID from database")
def get_task_db(task_id: int):
    row = repository.get_task(task_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return row


@app.post("/tasks", status_code=201, summary="Create a new task in database")
def create_task(body: TaskCreate):
    if not body.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    return repository.create_task(body.title)


@app.put("/tasks/{task_id}")
def update_task(task_id: int, body: TaskUpdate):
    try:
        row = repository.update_task(task_id, body.title, body.done)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return {"id": task_id, "title": row["title"], "done": row["done"]}


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    try:
        repository.delete_task(task_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return Response(status_code=204)