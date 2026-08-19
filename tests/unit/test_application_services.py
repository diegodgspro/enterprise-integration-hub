"""Unit tests for transport-independent application services."""
from datetime import date, datetime, timedelta, timezone
import unittest
from uuid import UUID, uuid4

from app.application.commands import CreateAppointmentCommand, CreatePatientCommand, GetAppointmentCommand, GetPatientCommand, UpdatePatientCommand
from app.application.errors import AppointmentConflict, AppointmentNotFound, DuplicatePatient, InvalidAppointmentData, InvalidPatientData, PatientNotFound
from app.application.ports import AppointmentRepository, PatientRepository
from app.application.services import CreateAppointmentService, CreatePatientService, GetAppointmentService, GetPatientService, UpdatePatientService
from app.domain.entities.appointment import Appointment, AppointmentStatus
from app.domain.entities.patient import Patient

NOW = datetime(2030, 1, 1, 12, tzinfo=timezone.utc)
PATIENT_ID = UUID("11111111-1111-4111-8111-111111111111")
APPOINTMENT_ID = UUID("22222222-2222-4222-8222-222222222222")

class FakePatientRepository:
    def __init__(self, patients=()) -> None:
        self.patients = {patient.id: patient for patient in patients}
    def get_by_id(self, patient_id):
        return self.patients.get(patient_id)
    def get_by_cpf(self, cpf):
        return next((patient for patient in self.patients.values() if patient.cpf == cpf), None)
    def save(self, patient):
        self.patients[patient.id] = patient
    def list_all(self):
        return tuple(self.patients.values())

class FakeAppointmentRepository:
    def __init__(self, appointments=(), conflict=False) -> None:
        self.appointments = {item.id: item for item in appointments}
        self.conflict = conflict
    def get_by_id(self, appointment_id):
        return self.appointments.get(appointment_id)
    def save(self, appointment):
        self.appointments[appointment.id] = appointment
    def has_conflict(self, patient_id, appointment_date):
        return self.conflict or any(item.patient_id == patient_id and item.appointment_date == appointment_date for item in self.appointments.values())

def patient() -> Patient:
    return Patient(PATIENT_ID, "Ana Silva", "12345678901", date(1990, 5, 12), "ana@example.test", "+5511999990000", NOW, NOW)

def appointment() -> Appointment:
    return Appointment(APPOINTMENT_ID, PATIENT_ID, NOW + timedelta(days=1), "Cardiology", AppointmentStatus.SCHEDULED, NOW, NOW)

class RepositoryPortTests(unittest.TestCase):
    def test_fakes_implement_repository_ports(self) -> None:
        self.assertIsInstance(FakePatientRepository(), PatientRepository)
        self.assertIsInstance(FakeAppointmentRepository(), AppointmentRepository)
class CreatePatientServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository: PatientRepository = FakePatientRepository()
        self.command = CreatePatientCommand("Ana Silva", "12345678901", date(1990, 5, 12), "ana@example.test", "+5511999990000")

    def test_valid_creation_uses_generated_id_and_timestamps(self) -> None:
        result = CreatePatientService(self.repository, lambda: PATIENT_ID, lambda: NOW).execute(self.command)
        self.assertEqual(result.id, PATIENT_ID)
        self.assertEqual(result.created_at, NOW)
        self.assertEqual(result.updated_at, NOW)
        self.assertEqual(self.repository.get_by_id(PATIENT_ID).cpf, self.command.cpf)

    def test_duplicate_cpf(self) -> None:
        repository = FakePatientRepository([patient()])
        with self.assertRaises(DuplicatePatient):
            CreatePatientService(repository).execute(self.command)

    def test_invalid_data(self) -> None:
        command = CreatePatientCommand(" ", "12345678901", date(1990, 5, 12))
        with self.assertRaises(InvalidPatientData):
            CreatePatientService(self.repository).execute(command)

class GetPatientServiceTests(unittest.TestCase):
    def test_found(self) -> None:
        result = GetPatientService(FakePatientRepository([patient()])).execute(GetPatientCommand(PATIENT_ID))
        self.assertEqual(result.id, PATIENT_ID)

    def test_not_found(self) -> None:
        with self.assertRaises(PatientNotFound):
            GetPatientService(FakePatientRepository()).execute(GetPatientCommand(PATIENT_ID))

class UpdatePatientServiceTests(unittest.TestCase):
    def test_valid_update_changes_only_allowed_field_and_timestamp(self) -> None:
        repository = FakePatientRepository([patient()])
        later = NOW + timedelta(hours=1)
        result = UpdatePatientService(repository, lambda: later).execute(UpdatePatientCommand(PATIENT_ID, name="Ana Souza"))
        self.assertEqual(result.name, "Ana Souza")
        self.assertEqual(result.cpf, "12345678901")
        self.assertEqual(result.birth_date, date(1990, 5, 12))
        self.assertEqual(result.created_at, NOW)
        self.assertEqual(result.updated_at, later)

    def test_patient_not_found(self) -> None:
        with self.assertRaises(PatientNotFound):
            UpdatePatientService(FakePatientRepository()).execute(UpdatePatientCommand(PATIENT_ID, name="New Name"))

    def test_empty_update(self) -> None:
        with self.assertRaises(InvalidPatientData):
            UpdatePatientCommand(PATIENT_ID)

    def test_invalid_data_does_not_modify_persisted_patient(self) -> None:
        original = patient()
        repository = FakePatientRepository([original])
        with self.assertRaises(InvalidPatientData):
            UpdatePatientService(repository).execute(UpdatePatientCommand(PATIENT_ID, name=" "))
        self.assertIs(repository.get_by_id(PATIENT_ID), original)

    def test_cpf_cannot_be_supplied(self) -> None:
        with self.assertRaises(TypeError):
            UpdatePatientCommand(PATIENT_ID, cpf="99999999999")

class CreateAppointmentServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.patients = FakePatientRepository([patient()])
        self.appointments: AppointmentRepository = FakeAppointmentRepository()
        self.command = CreateAppointmentCommand(PATIENT_ID, NOW + timedelta(days=1), "Cardiology")

    def test_valid_creation_and_initial_status(self) -> None:
        result = CreateAppointmentService(self.patients, self.appointments, lambda: APPOINTMENT_ID, lambda: NOW).execute(self.command)
        self.assertEqual(result.id, APPOINTMENT_ID)
        self.assertEqual(result.status, AppointmentStatus.SCHEDULED)
        self.assertEqual(result.created_at, NOW)
        self.assertEqual(result.updated_at, NOW)

    def test_patient_not_found(self) -> None:
        with self.assertRaises(PatientNotFound):
            CreateAppointmentService(FakePatientRepository(), self.appointments).execute(self.command)

    def test_schedule_conflict(self) -> None:
        with self.assertRaises(AppointmentConflict):
            CreateAppointmentService(self.patients, FakeAppointmentRepository(conflict=True)).execute(self.command)

    def test_invalid_data(self) -> None:
        command = CreateAppointmentCommand(PATIENT_ID, NOW, " ")
        with self.assertRaises(InvalidAppointmentData):
            CreateAppointmentService(self.patients, self.appointments).execute(command)

class GetAppointmentServiceTests(unittest.TestCase):
    def test_found(self) -> None:
        result = GetAppointmentService(FakeAppointmentRepository([appointment()])).execute(GetAppointmentCommand(APPOINTMENT_ID))
        self.assertEqual(result.id, APPOINTMENT_ID)

    def test_not_found(self) -> None:
        with self.assertRaises(AppointmentNotFound):
            GetAppointmentService(FakeAppointmentRepository()).execute(GetAppointmentCommand(APPOINTMENT_ID))

if __name__ == "__main__":
    unittest.main()

