from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from app.adapters.rest.dependencies import Services, get_services
from app.application.commands.patient import CreatePatientCommand, GetPatientCommand, ListPatientsCommand, UpdatePatientCommand
from app.schemas.error import ErrorResponse
from app.schemas.patient import CreatePatientRequest, PatientListResponse, PatientResponse, UpdatePatientRequest

router = APIRouter(prefix='/patients', tags=['Patients'])
def error_models(*codes: int) -> dict:
    return {code: {'model': ErrorResponse} for code in codes}

@router.get('', response_model=PatientListResponse, response_model_exclude_none=True, responses=error_models(400, 422, 500))
def list_patients(limit: Annotated[int, Query(ge=1, le=100)] = 20, offset: Annotated[int, Query(ge=0)] = 0, services: Services = Depends(get_services)) -> PatientListResponse:
    result = services.list_patients.execute(ListPatientsCommand(limit, offset))
    return PatientListResponse(items=[PatientResponse.model_validate(item) for item in result.items], limit=result.limit, offset=result.offset, total=result.total)

@router.post('', response_model=PatientResponse, response_model_exclude_none=True, status_code=status.HTTP_201_CREATED, responses=error_models(400, 409, 422, 500))
def create_patient(body: CreatePatientRequest, services: Services = Depends(get_services)) -> PatientResponse:
    result = services.create_patient.execute(CreatePatientCommand(**body.model_dump()))
    return PatientResponse.model_validate(result)

@router.get('/{patient_id}', response_model=PatientResponse, response_model_exclude_none=True, responses=error_models(400, 404, 500))
def get_patient(patient_id: UUID, services: Services = Depends(get_services)) -> PatientResponse:
    return PatientResponse.model_validate(services.get_patient.execute(GetPatientCommand(patient_id)))

@router.put('/{patient_id}', response_model=PatientResponse, response_model_exclude_none=True, responses=error_models(400, 404, 422, 500))
def update_patient(patient_id: UUID, body: UpdatePatientRequest, services: Services = Depends(get_services)) -> PatientResponse:
    changes = body.model_dump(exclude_unset=True)
    return PatientResponse.model_validate(services.update_patient.execute(UpdatePatientCommand(patient_id, **changes)))
