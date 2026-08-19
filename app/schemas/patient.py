from datetime import date, datetime
from typing import Annotated, Optional
from uuid import UUID
from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StringConstraints, field_validator, model_validator
from pydantic.json_schema import WithJsonSchema

def validate_email(value: str) -> str:
    local, separator, domain = value.rpartition('@')
    if not separator or not local or '.' not in domain or domain.startswith('.') or domain.endswith('.'):
        raise ValueError('invalid email address')
    return value

Name = Annotated[str, StringConstraints(min_length=1, max_length=200)]
Cpf = Annotated[str, StringConstraints(pattern=r'^[0-9]{11}$')]
Phone = Annotated[str, StringConstraints(pattern=r'^\+[1-9][0-9]{7,14}$')]
Email = Annotated[str, StringConstraints(max_length=254), AfterValidator(validate_email), WithJsonSchema({'type': 'string', 'format': 'email', 'maxLength': 254})]
OptionalResponseEmail = Annotated[Optional[Email], WithJsonSchema({'type': 'string', 'format': 'email', 'maxLength': 254})]
OptionalResponsePhone = Annotated[Optional[Phone], WithJsonSchema({'type': 'string', 'pattern': r'^\+[1-9][0-9]{7,14}$'})]

class CreatePatientRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: Name
    cpf: Cpf
    birth_date: date
    email: Optional[Email] = None
    phone: Optional[Phone] = None
    @field_validator('email', 'phone', mode='before')
    @classmethod
    def reject_explicit_null(cls, value):
        if value is None:
            raise ValueError('field cannot be null')
        return value

class UpdatePatientRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', json_schema_extra={'minProperties': 1})
    name: Optional[Name] = None
    email: Optional[Email] = None
    phone: Optional[Phone] = None
    @field_validator('name', 'email', 'phone', mode='before')
    @classmethod
    def reject_explicit_null(cls, value):
        if value is None:
            raise ValueError('field cannot be null')
        return value
    @model_validator(mode='after')
    def at_least_one_field(self) -> 'UpdatePatientRequest':
        if not self.model_fields_set:
            raise ValueError('at least one field must be provided')
        return self

class PatientResponse(BaseModel):
    model_config = ConfigDict(extra='forbid', from_attributes=True)
    id: UUID
    name: Name
    cpf: Cpf
    birth_date: date
    email: OptionalResponseEmail = None
    phone: OptionalResponsePhone = None
    created_at: datetime
    updated_at: datetime

class PatientListResponse(BaseModel):
    model_config = ConfigDict(extra='forbid')
    items: list[PatientResponse]
    limit: Annotated[int, Field(ge=1)]
    offset: Annotated[int, Field(ge=0)]
    total: Annotated[int, Field(ge=0)]
