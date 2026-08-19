"""Appointment application result."""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from app.domain.entities.appointment import Appointment, AppointmentStatus

@dataclass(frozen=True)
class AppointmentResult:
    id: UUID
    patient_id: UUID
    appointment_date: datetime
    specialty: str
    status: AppointmentStatus
    created_at: datetime
    updated_at: datetime
    @classmethod
    def from_entity(cls, appointment: Appointment) -> "AppointmentResult":
        return cls(appointment.id, appointment.patient_id, appointment.appointment_date, appointment.specialty, appointment.status, appointment.created_at, appointment.updated_at)
