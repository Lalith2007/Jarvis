from fastapi import APIRouter

router = APIRouter(tags=["intelligence"])

@router.get("/athena/status")
def athena_status():
    return {"status": "healthy", "service": "athena"}

@router.get("/planner/status")
def planner_status():
    return {"status": "healthy", "service": "planner"}

@router.get("/executor/status")
def executor_status():
    return {"status": "healthy", "service": "executor"}

@router.get("/memory/status")
def memory_status():
    return {"status": "healthy", "service": "memory"}
