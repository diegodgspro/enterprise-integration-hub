"""Domain entities."""

from app.domain.entities.appointment import Appointment, AppointmentStatus
from app.domain.entities.patient import Patient

__all__ = ["Appointment", "AppointmentStatus", "Patient"]
