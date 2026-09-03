"""Unit tests for PostgreSQL persistence models and explicit mappings."""

from datetime import date, datetime, timedelta, timezone
import os
import unittest
from unittest.mock import MagicMock
from uuid import UUID

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.exc import OperationalError

from app.adapters.persistence.database import create_postgres_engine
from app.adapters.persistence.models import AppointmentModel, PatientModel
from app.adapters.persistence.repositories import (
    PostgresAppointmentRepository,
    PostgresPatientRepository,
    appointment_to_domain,
    appointment_to_model,
    patient_to_domain,
    patient_to_model,
)
from app.application.ports import AppointmentRepository, PatientRepository
from app.core.errors import InfrastructureError
from app.domain.entities.appointment import Appointment, AppointmentStatus
from app.domain.entities.patient import Patient
from app.main import create_app

NOW = datetime(2030, 1, 1, 12, 30, tzinfo=timezone(timedelta(hours=-3)))
PATIENT_ID = UUID("11111111-1111-4111-8111-111111111111")
APPOINTMENT_ID = UUID("22222222-2222-4222-8222-222222222222")


def patient() -> Patient:
    return Patient(
        PATIENT_ID, "Ana Silva", "12345678901", date(1990, 5, 12),
        "ana@example.test", "+5511999990000", NOW, NOW,
    )


def appointment() -> Appointment:
    return Appointment(
        APPOINTMENT_ID, PATIENT_ID, NOW + timedelta(days=1), "Cardiology",
        AppointmentStatus.CONFIRMED, NOW, NOW,
    )


class MappingTests(unittest.TestCase):
    def test_patient_round_trip_preserves_values_and_timezone(self) -> None:
        entity = patient()
        model = patient_to_model(entity)
        restored = patient_to_domain(model)
        self.assertEqual(restored, entity)
        self.assertIsNot(restored, entity)
        self.assertNotIsInstance(entity, PatientModel)
        self.assertIsNotNone(restored.created_at.tzinfo)

    def test_appointment_round_trip_preserves_enum_uuid_and_timezone(self) -> None:
        entity = appointment()
        model = appointment_to_model(entity)
        restored = appointment_to_domain(model)
        self.assertEqual(restored, entity)
        self.assertEqual(model.status, "CONFIRMED")
        self.assertIsInstance(restored.status, AppointmentStatus)
        self.assertIsNotNone(restored.appointment_date.tzinfo)


class MetadataTests(unittest.TestCase):
    def test_patient_cpf_has_named_unique_constraint(self) -> None:
        names = {
            constraint.name for constraint in PatientModel.__table__.constraints
            if isinstance(constraint, UniqueConstraint)
        }
        self.assertIn("uq_patients_cpf", names)

    def test_appointment_has_fk_index_and_status_check(self) -> None:
        patient_id = AppointmentModel.__table__.c.patient_id
        self.assertTrue(patient_id.index)
        self.assertEqual(next(iter(patient_id.foreign_keys)).target_fullname, "patients.id")
        names = {
            constraint.name for constraint in AppointmentModel.__table__.constraints
            if isinstance(constraint, CheckConstraint)
        }
        self.assertIn("ck_appointments_status", names)


class RepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = MagicMock()
        self.factory = MagicMock(return_value=self.session)
        self.patients = PostgresPatientRepository(self.factory)
        self.appointments = PostgresAppointmentRepository(self.factory)

    def test_patient_save_uses_merge_and_transaction_lifecycle(self) -> None:
        entity = patient()
        self.patients.save(entity)
        persisted = self.session.merge.call_args.args[0]
        self.assertIsInstance(persisted, PatientModel)
        self.assertEqual(persisted.id, entity.id)
        self.session.commit.assert_called_once_with()
        self.session.close.assert_called_once_with()

    def test_patient_lookups_and_list_map_models_to_domain(self) -> None:
        model = patient_to_model(patient())
        self.session.get.return_value = model
        self.assertEqual(self.patients.get_by_id(PATIENT_ID), patient())
        self.session.scalar.return_value = model
        self.assertEqual(self.patients.get_by_cpf("12345678901"), patient())
        self.session.scalars.return_value.all.return_value = [model]
        self.assertEqual(self.patients.list_all(), (patient(),))

    def test_appointment_save_lookup_and_conflict(self) -> None:
        entity = appointment()
        model = appointment_to_model(entity)
        self.appointments.save(entity)
        self.assertIsInstance(self.session.merge.call_args.args[0], AppointmentModel)
        self.session.get.return_value = model
        self.assertEqual(self.appointments.get_by_id(APPOINTMENT_ID), entity)
        self.session.scalar.return_value = APPOINTMENT_ID
        self.assertTrue(self.appointments.has_conflict(PATIENT_ID, entity.appointment_date))
        self.session.scalar.return_value = None
        self.assertFalse(self.appointments.has_conflict(PATIENT_ID, entity.appointment_date))

    def test_database_error_is_wrapped_and_session_is_rolled_back(self) -> None:
        self.session.get.side_effect = OperationalError("SELECT", {}, Exception("unavailable"))
        with self.assertRaises(InfrastructureError) as captured:
            self.patients.get_by_id(PATIENT_ID)
        self.assertIsInstance(captured.exception.__cause__, OperationalError)
        self.session.rollback.assert_called_once_with()
        self.session.close.assert_called_once_with()


class ConfigurationTests(unittest.TestCase):
    def test_engine_rejects_non_postgresql_url(self) -> None:
        with self.assertRaises(ValueError):
            create_postgres_engine("sqlite:///:memory:")

    def test_database_url_selects_postgres_repositories_without_connecting(self) -> None:
        old_value = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = "postgresql+psycopg://user:password@localhost/test_db"
        try:
            application = create_app()
        finally:
            if old_value is None:
                os.environ.pop("DATABASE_URL", None)
            else:
                os.environ["DATABASE_URL"] = old_value
        self.assertIsInstance(application.state.patient_repository, PostgresPatientRepository)
        self.assertIsInstance(application.state.appointment_repository, PostgresAppointmentRepository)
        self.assertIsInstance(application.state.patient_repository, PatientRepository)
        self.assertIsInstance(application.state.appointment_repository, AppointmentRepository)
        application.state.database_engine.dispose()


if __name__ == "__main__":
    unittest.main()
