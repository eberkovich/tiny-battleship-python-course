from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class RunResult:
    status: str
    code: str
    message: str
    technical_details: str = ""

    @property
    def passed(self) -> bool:
        return self.status == "passed"

    def to_dict(self) -> dict[str, str]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "RunResult":
        return cls(
            status=str(data["status"]),
            code=str(data["code"]),
            message=str(data["message"]),
            technical_details=str(data.get("technical_details", "")),
        )

