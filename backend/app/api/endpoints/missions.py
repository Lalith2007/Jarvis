from typing import List

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from app.mission.controller import mission_controller
from app.mission.models import Mission, MissionPriority
from app.mission.service import mission_service

router = APIRouter(prefix="/mission", tags=["mission"])

class CreateMissionRequest(BaseModel):
    goal: str
    priority: MissionPriority = MissionPriority.NORMAL

@router.get("", response_model=List[Mission])
def get_missions():
    return mission_service.all()

@router.get("/{mission_id}", response_model=Mission)
def get_mission(mission_id: str):
    mission = mission_service.get(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission

@router.post("", response_model=dict)
def create_mission(request: CreateMissionRequest, background_tasks: BackgroundTasks):
    # Run the mission in the background so the API doesn't block.
    # We aren't returning the full mission because controller.run does create internally.
    # However, to return the mission ID, we should perhaps create it first?
    # Wait, controller.run creates the mission internally. If we want to return the mission immediately,
    # we would need to separate create from run. But controller.run() does both.
    
    background_tasks.add_task(mission_controller.run, request.goal)
    return {"status": "started", "goal": request.goal}
