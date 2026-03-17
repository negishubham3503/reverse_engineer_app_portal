import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app
from app.repositories.task_repository import get_task, update_task

client = TestClient(app)

def test_list_methods_success():
    """Test getting methods for an existing app cleanly (Requirement: List available methods)"""
    response = client.get("/methods?app=OLX")
    assert response.status_code == 200
    data = response.json()
    assert "methods" in data
    assert isinstance(data["methods"], list)
    assert "search_ads" in data["methods"]

def test_list_methods_app_not_found():
    """Test getting methods for a non-existent app"""
    response = client.get("/methods?app=UnknownApp123")
    assert response.status_code == 404
    assert response.json()["detail"] == "App not yet available for reverse engineering"

@patch("main.execute_olx_search")
def test_execute_method_background_task_creation(mock_execute):
    """Test executing a method returns a background task ID (Requirement: Execute and Background Tasks)"""
    
    payload = {
        "method": "search_ads",
        "app": "OLX",
        "params": {"search_term": "laptops"}
    }
    
    response = client.post("/execute", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "task_id" in data
    assert data["status"] == "queued"
    assert data["message"] == "Task is getting executed in the background"
    
    task_id = data["task_id"]
    
    task_db_data = get_task(task_id)
    assert task_db_data is not None
    assert task_db_data["status"] == "queued"

def test_get_task_status():
    """Test checking the status of a specific task"""

    mock_task_id = "test-uuid-1234-5678"
    update_task(mock_task_id, status="completed", result={"items": ["laptop 1", "laptop 2"]}, message="Success")
    
    response = client.get(f"/tasks/{mock_task_id}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["task_id"] == mock_task_id
    assert data["status"] == "completed"
    assert data["result"] == {"items": ["laptop 1", "laptop 2"]}
    assert data["message"] == "Success"

def test_get_invalid_task_status():
    """Test checking a task that does not exist"""
    response = client.get("/tasks/non-existent-task-id")
    assert response.status_code == 200
    data = response.json()
    
    assert data["task_id"] == "non-existent-task-id"
    assert data["status"] == "not found"