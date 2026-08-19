"""Patient application services."""
from dataclasses import replace
from datetime import datetime, timezone
from typing import Callable
from uuid import UUID, uuid4

from app.application.commands.patient import CreatePatientCommand, GetPatientCommand, ListPatientsCommand, UpdatePatientCommand
from app.application.errors import DuplicatePatient, InvalidPatientData, PatientNotFound
from app.application.ports import PatientRepository
from app.application.results.patient import PatientListResult, PatientResult
from app.domain.entities.patient import Patient
from app.domain.errors import InvalidPatient

IdGenerator = Callable[[], UUID]
Clock = Callable[[], datetime]

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class CreatePatientService:
    def __init__(self, repository: PatientRepository, id_generator: IdGenerator = uuid4, clock: Clock = utc_now) -> None:
        self._repository = repository
        self._id_generator = id_generator
        self._clock = clock

    def execute(self, command: CreatePatientCommand) -> PatientResult:
        if self._repository.get_by_cpf(command.cpf) is not None:
            raise DuplicatePatient("a patient with this CPF already exists")
        now = self._clock()
        try:
            patient = Patient(
                id=self._id_generator(), name=command.name, cpf=command.cpf,
                birth_date=command.birth_date, email=command.email, phone=command.phone,
                created_at=now, updated_at=now,
            )
        except InvalidPatient as error:
            raise InvalidPatientData(str(error)) from error
        self._repository.save(patient)
        return PatientResult.from_entity(patient)

class GetPatientService:
    def __init__(self, repository: PatientRepository) -> None:
        self._repository = repository

    def execute(self, command: GetPatientCommand) -> PatientResult:
        patient = self._repository.get_by_id(command.patient_id)
        if patient is None:
            raise PatientNotFound("patient was not found")
        return PatientResult.from_entity(patient)

class ListPatientsService:
    def __init__(self, repository: PatientRepository) -> None:
        self._repository = repository

    def execute(self, command: ListPatientsCommand) -> PatientListResult:
        patients = self._repository.list_all()
        page = patients[command.offset:command.offset + command.limit]
        return PatientListResult(tuple(PatientResult.from_entity(patient) for patient in page), command.limit, command.offset, len(patients))

class UpdatePatientService:
    def __init__(self, repository: PatientRepository, clock: Clock = utc_now) -> None:
        self._repository = repository
        self._clock = clock

    def execute(self, command: UpdatePatientCommand) -> PatientResult:
        patient = self._repository.get_by_id(command.patient_id)
        if patient is None:
            raise PatientNotFound("patient was not found")
        changes = {"updated_at": self._clock()}
        for field in ("name", "email", "phone"):
            value = getattr(command, field)
            if value is not None:
                changes[field] = value
        try:
            updated_patient = replace(patient, **changes)
        except InvalidPatient as error:
            raise InvalidPatientData(str(error)) from error
        self._repository.save(updated_patient)
        return PatientResult.from_entity(updated_patient)
