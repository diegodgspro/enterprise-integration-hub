"""Patient application result."""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from uuid import UUID
from app.domain.entities.patient import Patient

@dataclass(frozen=True)
class PatientResult:
    id: UUID
    name: str
    cpf: str
    birth_date: date
    email: Optional[str]
    phone: Optional[str]
    created_at: datetime
    updated_at: datetime
    @classmethod
    def from_entity(cls, patient: Patient) -> "PatientResult":
        return cls(patient.id, patient.name, patient.cpf, patient.birth_date, patient.email, patient.phone, patient.created_at, patient.updated_at)
