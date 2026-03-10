from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ApplicationError(Exception):
    message: str
    code: str = "application_error"
    exit_code: int = 1
    details: dict[str, object] = field(default_factory=dict)

    def to_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {"error": self.code, "message": self.message}
        if self.details:
            payload["details"] = self.details
        return payload


class ConfigurationError(ApplicationError):
    code = "configuration_error"

    def __init__(self, message: str, *, details: dict[str, object] | None = None, exit_code: int = 2, code: str | None = None):
        super().__init__(
            message=message,
            code=code or self.code,
            exit_code=exit_code,
            details=details or {},
        )


class CommandExecutionError(ApplicationError):
    code = "command_execution_error"

    def __init__(self, message: str, *, details: dict[str, object] | None = None, exit_code: int = 1, code: str | None = None):
        super().__init__(
            message=message,
            code=code or self.code,
            exit_code=exit_code,
            details=details or {},
        )
