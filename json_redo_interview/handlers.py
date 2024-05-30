from abc import ABC, abstractmethod
from inspect import Traceback
from typing import TYPE_CHECKING, Self

from loguru import logger
from pydantic import ValidationError

from json_redo_interview.enums import EventTypes
from json_redo_interview.schemas import EventSchema

if TYPE_CHECKING:
    from json_redo_interview.db import FakeDB


class HandlerBase(ABC):
    def __init__(self, db_session: "FakeDB", data: dict[str, str | None]) -> None:
        self.data = data
        self.db_session = db_session

    @abstractmethod
    def send(self) -> None:
        pass

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: type[Exception] | None, exc_val: Exception | None, exc_tb: Traceback | None) -> None:
        if exc_val:
            self.db_session.insert_failed(self.data, reason=str(exc_val))


class SMSHandler(HandlerBase):
    def __init__(self, db_session: "FakeDB", data: dict[str, str | None]) -> None:
        self.phone = data["phone"]
        super().__init__(db_session, data)

    def send(self) -> None:
        logger.info("SMS sent to {}. Data: {}", self.phone, self.data)


class EmailHandler(HandlerBase):
    def __init__(self, db_session: "FakeDB", data: dict[str, str | None]) -> None:
        self.email = data["email"]
        super().__init__(db_session, data)

    def send(self) -> None:
        logger.info("Email sent to {}. Data: {}", self.email, self.data)


class PostHandler(HandlerBase):
    def __init__(self, db_session: "FakeDB", data: dict[str, str | None]) -> None:
        self.url = data["url"]
        super().__init__(db_session, data)

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
        with handler(db, validated.model_dump()) as sender:
            sender.send()
    else:
        db.insert_failed(event, reason=f"Unknown event type '{validated.event_type}'")
