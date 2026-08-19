"""Patient domain entity."""

from dataclasses import dataclass
from datetime import date, datetime
import re
from typing import Optional
from uuid import UUID

from app.domain.errors import InvalidPatient


_CPF_PATTERN = re.compile(r"^[0-9]{11}$")
_PHONE_PATTERN = re.compile(r"^\+[1-9][0-9]{7,14}$")


@dataclass
class Patient:
    """A patient represented independently of transport and persistence."""

    id: UUID
    name: str
    cpf: str
    birth_date: date
    email: Optional[str]
    phone: Optional[str]
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.id, UUID):
            raise InvalidPatient("id must be a UUID")
        if not isinstance(self.name, str) or not self.name.strip():
            raise InvalidPatient("name must not be empty")
        if len(self.name) > 200:
            raise InvalidPatient("name must not exceed 200 characters")
        if not isinstance(self.cpf, str) or _CPF_PATTERN.fullmatch(self.cpf) is None:
            raise InvalidPatient("cpf must contain exactly 11 numeric digits")
        if not isinstance(self.birth_date, date) or isinstance(self.birth_date, datetime):
            raise InvalidPatient("birth_date must be a date")
        if self.email is not None:
            if not isinstance(self.email, str) or not self.email.strip():
                raise InvalidPatient("email must not be empty when provided")
            if len(self.email) > 254:
                raise InvalidPatient("email must not exceed 254 characters")
        if self.phone is not None and (
            not isinstance(self.phone, str)
            or _PHONE_PATTERN.fullmatch(self.phone) is None
        ):
            raise InvalidPatient("phone must use the E.164 international format")
        if not isinstance(self.created_at, datetime):
            raise InvalidPatient("created_at must be a datetime")
        if not isinstance(self.updated_at, datetime):
            raise InvalidPatient("updated_at must be a datetime")
