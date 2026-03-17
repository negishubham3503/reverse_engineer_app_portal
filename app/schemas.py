from pydantic import BaseModel

class AppInfo(BaseModel):
    app_name: str
    package_name: str

#available methods list
class MethodList(BaseModel):
    methods: list[str]

class MethodURLList(BaseModel):
    methods_with_url: dict[str, str]

#returned task response if the request takes longer to process
class TaskResponse(BaseModel):
    task_id: str
    status: str
    result: dict | None = None
    message: str

class ExecuteRequest(BaseModel):
    method: str
    app: str
    target_user: str | None = None
    params: dict[str, str] | None = None
