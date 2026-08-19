from dataclasses import dataclass
from fastapi import Request
from app.application.services.appointment import CreateAppointmentService, GetAppointmentService
from app.application.services.patient import CreatePatientService, GetPatientService, ListPatientsService, UpdatePatientService

@dataclass(frozen=True)
class Services:
    create_patient: CreatePatientService
    get_patient: GetPatientService
    list_patients: ListPatientsService
    update_patient: UpdatePatientService
    create_appointment: CreateAppointmentService
    get_appointment: GetAppointmentService

def get_services(request: Request) -> Services:
    return request.app.state.services
