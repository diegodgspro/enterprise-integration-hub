from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.application.errors import ApplicationError, AppointmentConflict, AppointmentNotFound, DuplicatePatient, InvalidAppointmentData, InvalidPatientData, PatientNotFound

def error_response(request: Request, status: int, code: str, message: str) -> JSONResponse:
    correlation_id = getattr(request.state, 'correlation_id', None)
    body = {'code': code, 'message': message, 'correlation_id': correlation_id}
    return JSONResponse(status_code=status, content=body)

async def validation_error_handler(request: Request, error: RequestValidationError) -> JSONResponse:
    errors = error.errors()
    malformed = any(item.get('type') == 'json_invalid' for item in errors)
    path_error = any(item.get('loc', (None,))[0] == 'path' for item in errors)
    status = 400 if malformed or path_error else 422
    code = 'BAD_REQUEST' if status == 400 else 'VALIDATION_ERROR'
    message = 'The request could not be parsed.' if malformed else 'One or more fields are invalid.'
    return error_response(request, status, code, message)

async def application_error_handler(request: Request, error: ApplicationError) -> JSONResponse:
    mappings = {
        InvalidPatientData: (400, 'VALIDATION_ERROR', 'One or more patient fields are invalid.'),
        InvalidAppointmentData: (400, 'VALIDATION_ERROR', 'One or more appointment fields are invalid.'),
        PatientNotFound: (404, 'PATIENT_NOT_FOUND', 'Patient was not found.'),
        AppointmentNotFound: (404, 'APPOINTMENT_NOT_FOUND', 'Appointment was not found.'),
        DuplicatePatient: (409, 'DUPLICATE_PATIENT', 'A patient with this CPF already exists.'),
        AppointmentConflict: (409, 'APPOINTMENT_CONFLICT', 'The requested appointment slot is unavailable.'),
    }
    status, code, message = mappings.get(type(error), (500, 'INTERNAL_ERROR', 'An unexpected error occurred.'))
    return error_response(request, status, code, message)

def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(ApplicationError, application_error_handler)
