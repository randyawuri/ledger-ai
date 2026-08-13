from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.schemas import ChatRequest, ChatResponse
from app.ai.service import AIService
from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.users.domain.models import User

router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    service = AIService(db)

    return service.chat(
        current_user,
        request.message,
    )