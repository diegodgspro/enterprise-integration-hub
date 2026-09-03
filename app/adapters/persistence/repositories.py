"""PostgreSQL implementations of application repository ports."""

from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.adapters.persistence.database import SessionFactory, session_scope
from app.adapters.persistence.models import AppointmentModel, PatientModel
from app.core.errors import InfrastructureError
from app.domain.entities.appointment import Appointment, AppointmentStatus
from app.domain.entities.patient import Patient


def patient_to_model(patient: Patient) -> PatientModel:
    return PatientModel(
        id=patient.id, name=patient.name, cpf=patient.cpf,
        birth_date=patient.birth_date, email=patient.email, phone=patient.phone,
        created_at=patient.created_at, updated_at=patient.updated_at,
    )


def patient_to_domain(model: PatientModel) -> Patient:
    return Patient(
        id=model.id, name=model.name, cpf=model.cpf,
        birth_date=model.birth_date, email=model.email, phone=model.phone,
        created_at=model.created_at, updated_at=model.updated_at,
    )


def appointment_to_model(appointment: Appointment) -> AppointmentModel:
    return AppointmentModel(
        id=appointment.id, patient_id=appointment.patient_id,
        appointment_date=appointment.appointment_date, specialty=appointment.specialty,
        status=appointment.status.value, created_at=appointment.created_at,
        updated_at=appointment.updated_at,
    )


def appointment_to_domain(model: AppointmentModel) -> Appointment:
    return Appointment(
        id=model.id, patient_id=model.patient_id,
        appointment_date=model.appointment_date, specialty=model.specialty,
        status=AppointmentStatus(model.status), created_at=model.created_at,
        updated_at=model.updated_at,
    )


class PostgresPatientRepository:
    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    def get_by_id(self, patient_id: UUID) -> Optional[Patient]:
        try:
            with session_scope(self._session_factory) as session:
                model = session.get(PatientModel, patient_id)
                return None if model is None else patient_to_domain(model)
        except SQLAlchemyError as error:
            raise InfrastructureError("patient lookup failed") from error

    def get_by_cpf(self, cpf: str) -> Optional[Patient]:
        try:
            with session_scope(self._session_factory) as session:
                model = session.scalar(select(PatientModel).where(PatientModel.cpf == cpf))
                return None if model is None else patient_to_domain(model)
        except SQLAlchemyError as error:
            raise InfrastructureError("patient lookup failed") from error

    def save(self, patient: Patient) -> None:
        try:
            with session_scope(self._session_factory) as session:
                session.merge(patient_to_model(patient))
        except SQLAlchemyError as error:
            raise InfrastructureError("patient save failed") from error

    def list_all(self) -> Sequence[Patient]:
        try:
            with session_scope(self._session_factory) as session:
                query = select(PatientModel).order_by(PatientModel.created_at, PatientModel.id)
                return tuple(patient_to_domain(model) for model in session.scalars(query).all())
        except SQLAlchemyError as error:
            raise InfrastructureError("patient list failed") from error


class PostgresAppointmentRepository:
    def __init__(self, session_factory: SessionFactory) -> None:
        self._session_factory = session_factory

    def get_by_id(self, appointment_id: UUID) -> Optional[Appointment]:
        try:
            with session_scope(self._session_factory) as session:
                model = session.get(AppointmentModel, appointment_id)
                return None if model is None else appointment_to_domain(model)
        except SQLAlchemyError as error:
            raise InfrastructureError("appointment lookup failed") from error

    def save(self, appointment: Appointment) -> None:
        try:
            with session_scope(self._session_factory) as session:
                session.merge(appointment_to_model(appointment))
        except SQLAlchemyError as error:
            raise InfrastructureError("appointment save failed") from error

    def has_conflict(self, patient_id: UUID, appointment_date: datetime) -> bool:
        try:
            with session_scope(self._session_factory) as session:
                query = select(AppointmentModel.id).where(
                    AppointmentModel.patient_id == patient_id,
                    AppointmentModel.appointment_date == appointment_date,
                ).limit(1)
                return session.scalar(query) is not None
        except SQLAlchemyError as error:
            raise InfrastructureError("appointment conflict lookup failed") from error
