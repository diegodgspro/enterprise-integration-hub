# Enterprise Integration Hub

A healthcare integration portfolio demonstrating how modern REST consumers and versioned SOAP contracts can share transport-independent business rules.

The project uses a ports-and-adapters architecture to keep domain and application logic independent from HTTP, JSON, XML, SOAP and database technologies.

## Current implementation status

| Capability | Status |
|---|---|
| FastAPI REST application | Implemented |
| Patient and appointment use cases | Implemented |
| In-memory repositories | Implemented |
| PostgreSQL repositories | Implemented |
| SQLAlchemy mappings | Implemented |
| Alembic migration | Implemented |
| Correlation ID middleware | Implemented |
| REST error mapping | Implemented |
| OpenAPI contract and examples | Versioned |
| WSDL, XSD and SOAP examples | Versioned |
| Executable SOAP adapter | Planned |
| Authentication and authorization | Planned |
| Docker and CI/CD | Planned |

> The REST and persistence layers are executable. SOAP is currently represented by versioned contracts and examples; no SOAP runtime endpoint is claimed.

## Business problem

Healthcare organizations often need to exchange information between legacy systems and modern applications. These systems may use different protocols, data formats and error models, increasing maintenance cost and the risk of inconsistent business rules.

Enterprise Integration Hub models an intermediary application in which REST and future SOAP adapters translate transport-specific messages into the same internal commands and results.

## Architecture

```mermaid
flowchart TB
    REST["REST / JSON"] --> RA["FastAPI adapter"]
    SOAP["SOAP / XML contracts"] -. planned runtime .-> SA["SOAP adapter"]
    RA --> APP["Application services"]
    SA --> APP
    APP --> DOMAIN["Domain"]
    APP --> PORTS["Repository ports"]
    PORTS --> MEM["In-memory adapter"]
    PORTS --> PG["PostgreSQL adapter"]
```

The domain and application layers do not depend on FastAPI, Pydantic, SQLAlchemy, PostgreSQL or SOAP libraries. Adapters translate requests, persistence records and errors at the system boundaries.

See [docs/architecture.md](docs/architecture.md) for implementation details and boundaries.

## Implemented REST API

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/patients` | List patients |
| `POST` | `/api/v1/patients` | Create a patient |
| `GET` | `/api/v1/patients/{patient_id}` | Retrieve a patient |
| `PUT` | `/api/v1/patients/{patient_id}` | Update a patient |
| `POST` | `/api/v1/appointments` | Create an appointment |
| `GET` | `/api/v1/appointments/{appointment_id}` | Retrieve an appointment |

The API returns consistent validation, not-found, conflict and internal-error payloads. Requests and responses include an `X-Correlation-ID`, preserving a valid caller-provided value or generating a UUID.

## Contract-first boundaries

| Interface | Artifact | Runtime status |
|---|---|---|
| REST | [OpenAPI](contracts/openapi/openapi.yaml) | Implemented with FastAPI |
| SOAP | [WSDL](contracts/soap/service.wsdl) | Contract only |
| XML | [Patient XSD](contracts/soap/xsd/patient.xsd) and [Appointment XSD](contracts/soap/xsd/appointment.xsd) | Contract only |

Request and response examples are available in [contracts/examples](contracts/examples/).

## Technology stack

- Python
- FastAPI and Pydantic
- SQLAlchemy 2
- PostgreSQL with psycopg
- Alembic
- OpenAPI 3
- WSDL and XSD
- Standard-library unittest and FastAPI TestClient

## Run locally

Create a virtual environment and install the dependencies:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
```

Start the API with the default in-memory repositories:

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the generated API documentation.

## PostgreSQL

Set a PostgreSQL connection string and apply the migration before starting the API:

```bash
export DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/integration_hub"
alembic upgrade head
uvicorn app.main:app --reload
```

Use the equivalent environment-variable syntax on Windows PowerShell. Without `DATABASE_URL`, the application intentionally uses in-memory repositories.

## Tests

```bash
python -m unittest discover -s tests -p "test*.py"
```

The current suite covers domain entities, transport-independent application services, REST behavior, validation and error semantics, correlation IDs, persistence mappings and PostgreSQL repository behavior with controlled test doubles.

## Contract consistency

REST and SOAP use different protocols while preserving shared rules for identifiers, required fields, limits and business errors. The executable SOAP adapter will map the same application errors to the faults already defined by the SOAP contract.

| REST | SOAP contract | Meaning |
|---|---|---|
| HTTP 404 `PATIENT_NOT_FOUND` | `PATIENT_NOT_FOUND` | Patient does not exist |
| HTTP 404 `APPOINTMENT_NOT_FOUND` | `APPOINTMENT_NOT_FOUND` | Appointment does not exist |
| HTTP 409 `DUPLICATE_PATIENT` | `DUPLICATE_PATIENT` | CPF is already registered |
| HTTP 409 `APPOINTMENT_CONFLICT` | `INVALID_APPOINTMENT` | Requested time is unavailable |
| HTTP 422 `VALIDATION_ERROR` | `INVALID_PATIENT` or `INVALID_APPOINTMENT` | Input violates the contract |
| HTTP 500 `INTERNAL_ERROR` | `INTERNAL_ERROR` | Internal failure without implementation details |

## Roadmap

- [x] Establish the repository and architectural boundaries
- [x] Version OpenAPI, WSDL and XSD contracts
- [x] Implement domain entities and application services
- [x] Implement the FastAPI REST adapter and error mapping
- [x] Add in-memory and PostgreSQL repository adapters
- [x] Add SQLAlchemy mappings and an Alembic migration
- [x] Add automated domain, application, REST and persistence tests
- [ ] Implement and validate the executable SOAP adapter
- [ ] Add authentication and authorization
- [ ] Add structured logging around the existing Correlation ID
- [ ] Add Docker, CI and reproducible PostgreSQL integration tests
- [ ] Publish a documented deployment and stable release

## Scope and data

Hospital Vida Integrada is a fictional scenario. All names, identifiers and examples are synthetic. This repository contains no employer code, credentials or real patient data.
