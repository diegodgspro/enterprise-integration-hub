"""Appointment domain entity."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from app.domain.errors import InvalidAppointment


class AppointmentStatus(str, Enum):
    """Statuses accepted by the REST and SOAP contracts."""

    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


@dataclass
class Appointment:
    """An appointment represented independently of external protocols."""

    id: UUID
    patient_id: UUID
    appointment_date: datetime
    specialty: str
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.id, UUID):
            raise InvalidAppointment("id must be a UUID")
        if not isinstance(self.patient_id, UUID):
            raise InvalidAppointment("patient_id must be a UUID")
        if not isinstance(self.appointment_date, datetime):
            raise InvalidAppointment("appointment_date must be a datetime")
        if not isinstance(self.specialty, str) or not self.specialty.strip():
            raise InvalidAppointment("specialty must not be empty")
        if len(self.specialty) > 100:
            raise InvalidAppointment("specialty must not exceed 100 characters")
        if not isinstance(self.status, AppointmentStatus):
            raise InvalidAppointment("status must be a valid AppointmentStatus")
        if not isinstance(self.created_at, datetime):
            raise InvalidAppointment("created_at must be a datetime")
        if not isinstance(self.updated_at, datetime):
            raise InvalidAppointment("updated_at must be a datetime")
