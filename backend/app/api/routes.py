from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse
from app.agents.hermes.service import hermes
router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
   response = hermes.chat(request.message)
   return ChatResponse(response=response)
