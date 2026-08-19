"""Transport-independent patient commands."""
from dataclasses import dataclass
from datetime import date
from typing import Optional
from uuid import UUID
from app.application.errors import InvalidPatientData

@dataclass(frozen=True)
class CreatePatientCommand:
    name: str
    cpf: str
    birth_date: date
    email: Optional[str] = None
    phone: Optional[str] = None

@dataclass(frozen=True)
class GetPatientCommand:
    patient_id: UUID

@dataclass(frozen=True)
class UpdatePatientCommand:
    patient_id: UUID
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    def __post_init__(self) -> None:
        if self.name is None and self.email is None and self.phone is None:
            raise InvalidPatientData("at least one field must be provided")
