"""Persistence adapters."""

from app.adapters.persistence.in_memory import (
    InMemoryAppointmentRepository,
    InMemoryPatientRepository,
)

__all__ = ["InMemoryAppointmentRepository", "InMemoryPatientRepository"]
