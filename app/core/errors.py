"""Technology-neutral errors used at adapter boundaries."""


class InfrastructureError(RuntimeError):
    """A technical dependency failed without exposing its implementation details."""
