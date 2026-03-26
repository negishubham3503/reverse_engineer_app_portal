import uuid
from fastapi import FastAPI, BackgroundTasks
from app.config.settings import settings
from app.services.methods_service import execute_method_with_app_access, execute_olx_search, get_method_names, execute_olx_search_direct
from app.schemas import MethodList, TaskResponse, ExecuteRequest
from app.repositories.task_repository import update_task, get_task
from app.util.bypass_security_controls import execute_ssl_pinning_bypass

app = FastAPI(
    title="Reverse Engineering APP portal",
    description="A portal for reverse engineering applications",
    version="1.0.0"
)
settings.resolve_paths()

task_db = {}

@app.get("/methods", response_model=MethodList)
def list_methods(app: str):
    methods = get_method_names(app, settings.get_methods_db_path())
    return MethodList(methods=methods)

@app.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    task = get_task(task_id)
    if not task:
        return TaskResponse(task_id=task_id, status="not found", message="Task not found")
    
    return TaskResponse(task_id=task_id, status=task["status"], result=task["result"], message=task["message"])

@app.post("/execute", response_model=TaskResponse)
async def execute_method(request: ExecuteRequest, background_tasks: BackgroundTasks):
    method = request.method
    app = request.app
    params = request.params

    task_id = str(uuid.uuid4())

    update_task(task_id, "queued", message="Task is queued for execution")

    # Add the execution of the method to the background tasks
    # Based on the app and method it can be routed to appropriate function.
    # New apps and methods would be added here as they are rev engineered.
    if app == "OLX":
        if method == "search_ads":
            background_tasks.add_task(execute_olx_search, task_id, params.get("search_term", ""))
        elif method == "method_with_app_access":
            background_tasks.add_task(execute_method_with_app_access)
    elif app == "instagram":
        if method == "search_users":
            #background_tasks.add_task(execute_instagram_search, task_id, method, params)
            pass

    return TaskResponse(task_id=task_id, status="queued", message="Task is getting executed in the background")

# just for testing the quick executing functions
# the logic is that if the backend api requires authentication tokens in the request headers then it is a time taking flow and it would be handled by the background tasks code
# if the api does not require authentication tokens and can be executed quickly then it can be directly awaited and the response can be sent back to the client without using the background tasks infrastructure.
@app.post("/execute/direct")
async def execute_method_direct(request: ExecuteRequest):
    """
    Directly awaits the execution to see if errors are happening in 
    the business logic rather than the background task infrastructure.
    """
    method = request.method
    app_name = request.app
    params = request.params or {}

    try:
        if app_name == "OLX" and method == "search_ads":
            result = await execute_olx_search_direct(params.get("search_term", ""))
            return {"status": "success", "result": result}
        if app_name == "OLX" and method == "method_with_app_access":
            result = execute_method_with_app_access()
            return {"status": "success", "result": result}
        else:
            return {"status": "error", "message": "Method or App not directly supported yet"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/execute_method_with_app_access")
def execute_method_with_app_access_endpoint(background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    update_task(task_id, "queued", message="Task is queued for execution")
    background_tasks.add_task(execute_method_with_app_access, task_id)
    return TaskResponse(task_id=task_id, status="queued", message="Task is getting executed in the background")

@app.get("/")
async def root():
    return {"message": "Hello World"}