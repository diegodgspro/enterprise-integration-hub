from fastapi import APIRouter
from app.adapters.rest.routes import appointments_router, health_router, patients_router

api_router = APIRouter(prefix='/api/v1')
api_router.include_router(health_router)
api_router.include_router(patients_router)
api_router.include_router(appointments_router)
