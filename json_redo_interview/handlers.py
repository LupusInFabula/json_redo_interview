from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from loguru import logger
from pydantic import ValidationError

from json_redo_interview.enums import EventTypes
from json_redo_interview.schemas import EventSchema

if TYPE_CHECKING:
    from json_redo_interview.db import FakeDB


class HandlerBase(ABC):
    @abstractmethod
    def __init__(self, data: dict[str, str | None]):
        pass

    @abstractmethod
    def send(self) -> None:
        pass


class SMSHandler(HandlerBase):
    def __init__(self, data: dict[str, str | None]):
        self.phone = data["phone"]
        self.data = data

    def send(self) -> None:
        logger.info("SMS sent to {}. Data: {}", self.phone, self.data)


class EmailHandler(HandlerBase):
    def __init__(self, data: dict[str, str | None]):
        self.email = data["email"]
        self.data = data

    def send(self) -> None:
        logger.info("Email sent to {}. Data: {}", self.email, self.data)


class PostHandler(HandlerBase):
    def __init__(self, data: dict[str, str | None]):
        self.url = data["url"]
        self.data = data

    def send(self) -> None:
        logger.info("POST sent to {}. Data: {}", self.url, self.data)


SENDER_MAP: dict[EventTypes, type[HandlerBase]] = {
    EventTypes.SMS: SMSHandler,
    EventTypes.EMAIL: EmailHandler,
    EventTypes.POST: PostHandler,
}


def process_event(event: dict, db: "FakeDB") -> None:
    try:
        validated = EventSchema(**event)
    except ValidationError as e:
        db.insert_failed(event, reason=str(e))
        return

    if handler := SENDER_MAP.get(validated.event_type):
        handler(validated.model_dump()).send()
    else:
        db.insert_failed(event, reason=f"Unknown event type '{validated.event_type}'")
