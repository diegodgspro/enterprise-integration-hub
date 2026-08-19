"""Framework-independent domain exceptions."""


class DomainError(ValueError):
    """Base exception for violations of domain invariants."""


class InvalidPatient(DomainError):
    """Raised when patient data violates a domain invariant."""


class InvalidAppointment(DomainError):
    """Raised when appointment data violates a domain invariant."""
