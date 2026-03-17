from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_ROOT: Path = Path(__file__).parent.parent.parent
    METHODS_DB_PATH: Path = PROJECT_ROOT / "database" / "app_details.json"
    ALLOWED_DATA_DIR: Path = PROJECT_ROOT / "database"

    TASKS_DB_PATH: Path = PROJECT_ROOT / "database" / "task.json"
    TASKS_LOCK_PATH: Path = PROJECT_ROOT / "database" / "task.json.lock"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    def resolve_paths(self):
        self.METHODS_DB_PATH = self.METHODS_DB_PATH.resolve()
        self.ALLOWED_DATA_DIR = self.ALLOWED_DATA_DIR.resolve()
        self.TASKS_DB_PATH = self.TASKS_DB_PATH.resolve()
        self.TASKS_LOCK_PATH = self.TASKS_LOCK_PATH.resolve()


    def get_methods_db_path(self):
        if not self.METHODS_DB_PATH.is_file():
            raise FileNotFoundError(f"Methods database file not found at {self.METHODS_DB_PATH}")
        return self.METHODS_DB_PATH

settings = Settings()