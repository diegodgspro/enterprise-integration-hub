'''Composition root for the Enterprise Integration Hub REST application.'''
import os
from typing import Optional
from uuid import uuid4
from fastapi import FastAPI, Request
from fastapi.openapi.utils import get_openapi
from app.adapters.persistence.in_memory import InMemoryAppointmentRepository, InMemoryPatientRepository
from app.adapters.persistence.database import create_postgres_engine, create_session_factory
from app.adapters.persistence.repositories import PostgresAppointmentRepository, PostgresPatientRepository
from app.adapters.rest.dependencies import Services
from app.adapters.rest.exception_handlers import register_exception_handlers
from app.adapters.rest.router import api_router
from app.application.services.appointment import CreateAppointmentService, GetAppointmentService
from app.application.services.patient import CreatePatientService, GetPatientService, ListPatientsService, UpdatePatientService
from app.application.ports import AppointmentRepository, PatientRepository

def create_app(patient_repository: Optional[PatientRepository] = None, appointment_repository: Optional[AppointmentRepository] = None) -> FastAPI:
    if (patient_repository is None) != (appointment_repository is None):
        raise ValueError('patient_repository and appointment_repository must be supplied together')
    database_url = os.getenv('DATABASE_URL')
    engine = None
    if patient_repository is not None and appointment_repository is not None:
        patients = patient_repository
        appointments = appointment_repository
    elif database_url:
        engine = create_postgres_engine(database_url)
        session_factory = create_session_factory(engine)
        patients = PostgresPatientRepository(session_factory)
        appointments = PostgresAppointmentRepository(session_factory)
    else:
        patients = InMemoryPatientRepository()
        appointments = InMemoryAppointmentRepository()
    application = FastAPI(title='Enterprise Integration Hub', description='API de integração do cenário fictício Hospital Vida Integrada.', version='0.1.0')
    application.state.patient_repository = patients
    application.state.appointment_repository = appointments
    application.state.database_engine = engine
    application.state.services = Services(
        CreatePatientService(patients), GetPatientService(patients), ListPatientsService(patients),
        UpdatePatientService(patients), CreateAppointmentService(patients, appointments), GetAppointmentService(appointments),
    )

    @application.middleware('http')
    async def correlation_id(request: Request, call_next):
        value = request.headers.get('X-Correlation-ID') or str(uuid4())
        request.state.correlation_id = value
        response = await call_next(request)
        response.headers['X-Correlation-ID'] = value
        return response

    register_exception_handlers(application)
    application.include_router(api_router)

    def custom_openapi() -> dict:
        if application.openapi_schema is None:
            schema = get_openapi(
                title=application.title,
                version=application.version,
                description=application.description,
                routes=application.routes,
            )
            for path in (
                '/api/v1/patients/{patient_id}',
                '/api/v1/appointments/{appointment_id}',
            ):
                schema['paths'][path]['get']['responses'].pop('422', None)
            application.openapi_schema = schema
        return application.openapi_schema

    application.openapi = custom_openapi
    return application

app = create_app()
