"""Appointment application services."""
from datetime import datetime, timezone
from typing import Callable
from uuid import UUID, uuid4

from app.application.commands.appointment import CreateAppointmentCommand, GetAppointmentCommand
from app.application.errors import AppointmentConflict, AppointmentNotFound, InvalidAppointmentData, PatientNotFound
from app.application.ports import AppointmentRepository, PatientRepository
from app.application.results import AppointmentResult
from app.domain.entities.appointment import Appointment, AppointmentStatus
from app.domain.errors import InvalidAppointment

IdGenerator = Callable[[], UUID]
Clock = Callable[[], datetime]

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class CreateAppointmentService:
    def __init__(self, patient_repository: PatientRepository, appointment_repository: AppointmentRepository, id_generator: IdGenerator = uuid4, clock: Clock = utc_now) -> None:
        self._patients = patient_repository
        self._appointments = appointment_repository
        self._id_generator = id_generator
        self._clock = clock

    def execute(self, command: CreateAppointmentCommand) -> AppointmentResult:
        if self._patients.get_by_id(command.patient_id) is None:
            raise PatientNotFound("patient was not found")
        if self._appointments.has_conflict(command.patient_id, command.appointment_date):
            raise AppointmentConflict("the requested appointment slot is unavailable")
        now = self._clock()
        try:
            appointment = Appointment(
                id=self._id_generator(), patient_id=command.patient_id,
                appointment_date=command.appointment_date, specialty=command.specialty,
                status=AppointmentStatus.SCHEDULED, created_at=now, updated_at=now,
            )
        except InvalidAppointment as error:
            raise InvalidAppointmentData(str(error)) from error
        self._appointments.save(appointment)
        return AppointmentResult.from_entity(appointment)

class GetAppointmentService:
    def __init__(self, repository: AppointmentRepository) -> None:
        self._repository = repository

    def execute(self, command: GetAppointmentCommand) -> AppointmentResult:
        appointment = self._repository.get_by_id(command.appointment_id)
        if appointment is None:
            raise AppointmentNotFound("appointment was not found")
        return AppointmentResult.from_entity(appointment)
