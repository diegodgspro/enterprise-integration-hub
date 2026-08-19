from datetime import datetime, timezone
import unittest
from uuid import UUID
from fastapi.testclient import TestClient
from app.main import create_app

PATIENT = {'name': 'Ana Silva', 'cpf': '12345678901', 'birth_date': '1990-05-12', 'email': 'ana@example.test', 'phone': '+5511999990000'}
DATE = '2030-09-20T14:30:00-03:00'

class RestApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(create_app())

    def create_patient(self, **changes):
        body = {**PATIENT, **changes}
        return self.client.post('/api/v1/patients', json=body)

    def test_health(self):
        response = self.client.get('/api/v1/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'healthy'})

    def test_create_patient(self):
        response = self.create_patient()
        self.assertEqual(response.status_code, 201)
        UUID(response.json()['id'])

    def test_patient_response_omits_absent_optional_fields(self):
        response = self.client.post('/api/v1/patients', json={key: PATIENT[key] for key in ('name', 'cpf', 'birth_date')})
        self.assertEqual(response.status_code, 201)
        self.assertNotIn('email', response.json())
        self.assertNotIn('phone', response.json())

    def test_invalid_patient(self):
        response = self.create_patient(cpf='invalid')
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()['code'], 'VALIDATION_ERROR')

    def test_duplicate_patient(self):
        self.create_patient()
        response = self.create_patient()
        self.assertEqual(response.status_code, 409)

    def test_get_existing_and_missing_patient(self):
        patient_id = self.create_patient().json()['id']
        self.assertEqual(self.client.get(f'/api/v1/patients/{patient_id}').status_code, 200)
        self.assertEqual(self.client.get('/api/v1/patients/11111111-1111-4111-8111-111111111111').status_code, 404)

    def test_update_patient(self):
        patient_id = self.create_patient().json()['id']
        response = self.client.put(f'/api/v1/patients/{patient_id}', json={'name': 'Ana Souza'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['name'], 'Ana Souza')

    def test_empty_update(self):
        patient_id = self.create_patient().json()['id']
        self.assertEqual(self.client.put(f'/api/v1/patients/{patient_id}', json={}).status_code, 422)

    def test_invalid_path_uuid(self):
        response = self.client.get('/api/v1/patients/not-a-uuid')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['code'], 'BAD_REQUEST')

    def test_list_patients(self):
        self.create_patient()
        response = self.client.get('/api/v1/patients?limit=10&offset=0')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['total'], 1)

    def test_create_and_get_appointment(self):
        patient_id = self.create_patient().json()['id']
        response = self.client.post('/api/v1/appointments', json={'patient_id': patient_id, 'appointment_date': DATE, 'specialty': 'Cardiology'})
        self.assertEqual(response.status_code, 201)
        appointment_id = response.json()['id']
        self.assertEqual(self.client.get(f'/api/v1/appointments/{appointment_id}').status_code, 200)

    def test_appointment_patient_not_found(self):
        response = self.client.post('/api/v1/appointments', json={'patient_id': '11111111-1111-4111-8111-111111111111', 'appointment_date': DATE, 'specialty': 'Cardiology'})
        self.assertEqual(response.status_code, 404)

    def test_appointment_conflict(self):
        patient_id = self.create_patient().json()['id']
        body = {'patient_id': patient_id, 'appointment_date': DATE, 'specialty': 'Cardiology'}
        self.client.post('/api/v1/appointments', json=body)
        self.assertEqual(self.client.post('/api/v1/appointments', json=body).status_code, 409)

    def test_missing_appointment(self):
        self.assertEqual(self.client.get('/api/v1/appointments/22222222-2222-4222-8222-222222222222').status_code, 404)

    def test_correlation_id_is_preserved(self):
        value = '33333333-3333-4333-8333-333333333333'
        self.assertEqual(self.client.get('/api/v1/health', headers={'X-Correlation-ID': value}).headers['X-Correlation-ID'], value)

    def test_correlation_id_is_generated(self):
        value = self.client.get('/api/v1/health').headers['X-Correlation-ID']
        UUID(value)

    def test_openapi_matches_validation_status_contract(self):
        schema = self.client.app.openapi()
        self.assertNotIn('422', schema['paths']['/api/v1/patients/{patient_id}']['get']['responses'])
        self.assertNotIn('422', schema['paths']['/api/v1/appointments/{appointment_id}']['get']['responses'])
        for path, method in (
            ('/api/v1/patients', 'get'),
            ('/api/v1/patients', 'post'),
            ('/api/v1/patients/{patient_id}', 'put'),
            ('/api/v1/appointments', 'post'),
        ):
            self.assertIn('422', schema['paths'][path][method]['responses'])

    def test_openapi_patient_optional_fields_are_not_nullable(self):
        patient = self.client.app.openapi()['components']['schemas']['PatientResponse']
        self.assertNotIn('email', patient['required'])
        self.assertNotIn('phone', patient['required'])
        self.assertEqual(patient['properties']['email']['type'], 'string')
        self.assertEqual(patient['properties']['phone']['type'], 'string')
        self.assertNotIn('nullable', patient['properties']['email'])
        self.assertNotIn('nullable', patient['properties']['phone'])
        self.assertNotIn('anyOf', patient['properties']['email'])
        self.assertNotIn('anyOf', patient['properties']['phone'])

if __name__ == '__main__':
    unittest.main()
