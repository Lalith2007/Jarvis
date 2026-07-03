from fastapi import APIRouter

from app.agents.hermes.service import hermes
from app.models.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    response = hermes.chat(request.message)
    return ChatResponse(response=response)
