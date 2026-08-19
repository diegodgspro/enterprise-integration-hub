'''Process-local persistence adapters.'''
from datetime import datetime
from threading import RLock
from typing import Optional, Sequence
from uuid import UUID
from app.domain.entities.appointment import Appointment
from app.domain.entities.patient import Patient

class InMemoryPatientRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, Patient] = {}
        self._lock = RLock()
    def get_by_id(self, patient_id: UUID) -> Optional[Patient]:
        with self._lock: return self._items.get(patient_id)
    def get_by_cpf(self, cpf: str) -> Optional[Patient]:
        with self._lock: return next((x for x in self._items.values() if x.cpf == cpf), None)
    def save(self, patient: Patient) -> None:
        with self._lock: self._items[patient.id] = patient
    def list_all(self) -> Sequence[Patient]:
        with self._lock: return tuple(self._items.values())
    def clear(self) -> None:
        with self._lock: self._items.clear()

class InMemoryAppointmentRepository:
    def __init__(self) -> None:
        self._items: dict[UUID, Appointment] = {}
        self._lock = RLock()
    def get_by_id(self, appointment_id: UUID) -> Optional[Appointment]:
        with self._lock: return self._items.get(appointment_id)
    def save(self, appointment: Appointment) -> None:
        with self._lock: self._items[appointment.id] = appointment
    def has_conflict(self, patient_id: UUID, appointment_date: datetime) -> bool:
        with self._lock: return any(x.patient_id == patient_id and x.appointment_date == appointment_date for x in self._items.values())
    def clear(self) -> None:
        with self._lock: self._items.clear()
