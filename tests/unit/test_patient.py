"""Unit tests for the Patient entity."""

from datetime import date, datetime, timezone
import unittest
from uuid import uuid4

from app.domain.entities.patient import Patient
from app.domain.errors import InvalidPatient


class PatientTests(unittest.TestCase):
    def _valid_data(self) -> dict:
        now = datetime.now(timezone.utc)
        return {
            "id": uuid4(),
            "name": "Ana Silva",
            "cpf": "12345678901",
            "birth_date": date(1990, 5, 12),
            "email": "ana.silva@example.test",
            "phone": "+5511999990000",
            "created_at": now,
            "updated_at": now,
        }

    def test_valid_patient(self) -> None:
        patient = Patient(**self._valid_data())

        self.assertEqual(patient.name, "Ana Silva")

    def test_empty_name_is_invalid(self) -> None:
        data = self._valid_data()
        data["name"] = "   "

        with self.assertRaises(InvalidPatient):
            Patient(**data)

    def test_invalid_cpf_is_rejected(self) -> None:
        data = self._valid_data()
        data["cpf"] = "123.456.789-01"

        with self.assertRaises(InvalidPatient):
            Patient(**data)

    def test_datetime_birth_date_is_rejected(self) -> None:
        data = self._valid_data()
        data["birth_date"] = datetime(1990, 5, 12, tzinfo=timezone.utc)

        with self.assertRaises(InvalidPatient):
            Patient(**data)

    def test_invalid_phone_is_rejected(self) -> None:
        data = self._valid_data()
        data["phone"] = "5511999990000"

        with self.assertRaises(InvalidPatient):
            Patient(**data)


if __name__ == "__main__":
    unittest.main()
