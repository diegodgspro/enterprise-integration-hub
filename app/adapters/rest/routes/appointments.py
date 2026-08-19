from uuid import UUID
from fastapi import APIRouter, Depends, status
from app.adapters.rest.dependencies import Services, get_services
from app.application.commands.appointment import CreateAppointmentCommand, GetAppointmentCommand
from app.schemas.appointment import AppointmentResponse, CreateAppointmentRequest
from app.schemas.error import ErrorResponse

router = APIRouter(prefix='/appointments', tags=['Appointments'])
def error_models(*codes: int) -> dict:
    return {code: {'model': ErrorResponse} for code in codes}

@router.post('', response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED, responses=error_models(400, 404, 409, 422, 500))
def create_appointment(body: CreateAppointmentRequest, services: Services = Depends(get_services)) -> AppointmentResponse:
    result = services.create_appointment.execute(CreateAppointmentCommand(**body.model_dump()))
    return AppointmentResponse.model_validate(result)

@router.get('/{appointment_id}', response_model=AppointmentResponse, responses=error_models(400, 404, 500))
def get_appointment(appointment_id: UUID, services: Services = Depends(get_services)) -> AppointmentResponse:
    return AppointmentResponse.model_validate(services.get_appointment.execute(GetAppointmentCommand(appointment_id)))
