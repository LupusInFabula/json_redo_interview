from typing import Self

from pydantic import BaseModel, EmailStr, Field, HttpUrl, StrictStr, model_validator

from json_redo_interview.enums import EventTypes


class EventSchema(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr | None
    phone: StrictStr | None = Field(None, min_length=6, max_length=67)
    url: HttpUrl | None
    event_type: EventTypes = Field(..., alias="type")

    _OPTIONALLY_REQUIRED: dict[EventTypes, list[str]] = {
        EventTypes.SMS: ["phone"],
        EventTypes.EMAIL: ["email"],
        EventTypes.POST: ["url"],
    }

    @model_validator(mode="after")
    def validate_event_type(self) -> Self:
        for field in self._OPTIONALLY_REQUIRED.get(self.event_type, []):
            if getattr(self, field) is None:
                raise ValueError(f"field '{field}' is required for {self.event_type} type events.")

        return self
