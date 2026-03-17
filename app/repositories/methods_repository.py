import json
from pathlib import Path
from fastapi import HTTPException

def get_methods_from_db(methods_db_path: Path) -> dict[str, dict[str, str]]:
    try:
        with methods_db_path.open("r", encoding="utf-8") as f:
            methods_db_data = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Methods database file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding methods database file")
    
    return methods_db_data