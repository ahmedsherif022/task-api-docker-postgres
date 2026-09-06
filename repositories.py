from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


class TaskRepository:
    """Repository interface for task data access."""

    def list_tasks(self) -> List[dict]:
        raise NotImplementedError

    def get_task(self, task_id: int) -> Optional[dict]:
        raise NotImplementedError

    def create_task(self, title: str) -> dict:
        raise NotImplementedError

    def update_task(self, task_id: int, title: str | None, done: bool | None) -> dict:
        raise NotImplementedError

    def delete_task(self, task_id: int) -> None:
        raise NotImplementedError


class PostgresTaskRepository(TaskRepository):
    """Postgres-backed implementation of TaskRepository."""

    def __init__(self, connection_string: str) -> None:
        self._connection_string = connection_string

    def _connect(self):
        return psycopg2.connect(self._connection_string)

    def list_tasks(self) -> List[dict]:
        conn = self._connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM tasks ORDER BY id")
                rows = cur.fetchall()
                return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_task(self, task_id: int) -> Optional[dict]:
        conn = self._connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
                row = cur.fetchone()
                return dict(row) if row else None
        finally:
            conn.close()

    def create_task(self, title: str) -> dict:
        conn = self._connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *",
                    (title, False),
                )
                row = cur.fetchone()
                conn.commit()
                return dict(row)
        finally:
            conn.close()

    def update_task(self, task_id: int, title: str | None, done: bool | None) -> dict:
        conn = self._connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Get current row to fill in None fields
                cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
                row = cur.fetchone()
                if row is None:
                    raise ValueError(f"Task {task_id} not found")

                current_title = row["title"]
                current_done = row["done"]

                final_title = title if title is not None else current_title
                final_done = done if done is not None else current_done

                cur.execute(
                    "UPDATE tasks SET title = %s, done = %s WHERE id = %s",
                    (final_title, final_done, task_id),
                )
                conn.commit()

                # Return updated row
                cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
                updated = cur.fetchone()
                return dict(updated)
        finally:
            conn.close()

    def delete_task(self, task_id: int) -> None:
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
                if cur.fetchone() is None:
                    raise ValueError(f"Task {task_id} not found")
                cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
                conn.commit()
        finally:
            conn.close()