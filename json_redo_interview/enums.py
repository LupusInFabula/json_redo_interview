from enum import StrEnum


class EventTypes(StrEnum):
    SMS = "sms"
    EMAIL = "email"
    POST = "post"

    @property
    def required_fields(self) -> list[str]:
        match self:
            case EventTypes.SMS:
                return ["phone"]
            case EventTypes.EMAIL:
                return ["email"]
            case EventTypes.POST:
                return ["url"]
            case _:
                raise ValueError(f"Unknown event type: {self}")
