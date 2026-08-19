from typing import Literal
from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict
from app.schemas.error import ErrorResponse

router = APIRouter(tags=['Health'])

class HealthResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    status: Literal['healthy']

@router.get('/health', response_model=HealthResponse, responses={500: {'model': ErrorResponse}})
def health() -> HealthResponse:
    return HealthResponse(status='healthy')
