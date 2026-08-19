from app.adapters.rest.routes.appointments import router as appointments_router
from app.adapters.rest.routes.health import router as health_router
from app.adapters.rest.routes.patients import router as patients_router

__all__ = ['appointments_router', 'health_router', 'patients_router']
