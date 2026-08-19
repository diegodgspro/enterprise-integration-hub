"""Unit tests for the Appointment entity."""

from datetime import datetime, timezone
import unittest
from uuid import uuid4

from app.domain.entities.appointment import Appointment, AppointmentStatus
from app.domain.errors import InvalidAppointment


class AppointmentTests(unittest.TestCase):
    def _valid_data(self) -> dict:
        now = datetime.now(timezone.utc)
        return {
            "id": uuid4(),
            "patient_id": uuid4(),
            "appointment_date": datetime(2030, 9, 20, 17, 30, tzinfo=timezone.utc),
            "specialty": "Cardiology",
            "status": AppointmentStatus.SCHEDULED,
            "created_at": now,
            "updated_at": now,
        }

    def test_valid_appointment(self) -> None:
        appointment = Appointment(**self._valid_data())

        self.assertEqual(appointment.status, AppointmentStatus.SCHEDULED)

    def test_empty_specialty_is_invalid(self) -> None:
        data = self._valid_data()
        data["specialty"] = "   "

        with self.assertRaises(InvalidAppointment):
            Appointment(**data)

    def test_invalid_status_is_rejected(self) -> None:
        data = self._valid_data()
        data["status"] = "PENDING"

        with self.assertRaises(InvalidAppointment):
            Appointment(**data)


if __name__ == "__main__":
    unittest.main()
