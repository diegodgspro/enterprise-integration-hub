"""Transport-independent appointment commands."""
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass(frozen=True)
class CreateAppointmentCommand:
    patient_id: UUID
    appointment_date: datetime
    specialty: str

@dataclass(frozen=True)
class GetAppointmentCommand:
    appointment_id: UUID
