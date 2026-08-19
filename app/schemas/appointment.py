from datetime import datetime
from typing import Annotated
from uuid import UUID
from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator
from app.domain.entities.appointment import AppointmentStatus

Specialty = Annotated[str, StringConstraints(min_length=1, max_length=100)]

class CreateAppointmentRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    patient_id: UUID
    appointment_date: datetime
    specialty: Specialty
    @field_validator('appointment_date')
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError('appointment_date must include a timezone offset')
        return value

class AppointmentResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)
    id: UUID
    patient_id: UUID
    appointment_date: datetime
    specialty: Specialty
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime
