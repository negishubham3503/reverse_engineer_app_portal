import json
from pathlib import Path
from filelock import FileLock
from app.config.settings import settings

def init_db():
    settings.TASKS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not settings.TASKS_DB_PATH.exists():
        with settings.TASKS_DB_PATH.open("w", encoding="utf-8") as f:
            json.dump({}, f)

def get_task(task_id: str) -> dict | None:
    init_db()
    with settings.TASKS_DB_PATH.open("r", encoding="utf-8") as f:
        tasks = json.load(f)
    return tasks.get(task_id)

def update_task(task_id: str, status: str, result: dict | None = None, message: str = ""):
    init_db()
    with FileLock(settings.TASKS_LOCK_PATH):
        with settings.TASKS_DB_PATH.open("r", encoding="utf-8") as f:
            tasks = json.load(f)
        
        tasks[task_id] = {"status": status, "result": result, "message": message}
        
        with settings.TASKS_DB_PATH.open("w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=4)