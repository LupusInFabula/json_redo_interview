from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from loguru import logger
from pydantic import ValidationError

from json_redo_interview.enums import EventTypes
from json_redo_interview.schemas import EventSchema

if TYPE_CHECKING:
    from json_redo_interview.db import FakeDB


class HandlerBase(ABC):
    def __init__(self, data: dict[str, str | None]) -> None:
        self.data = data

    @abstractmethod
    def send(self) -> None:
        pass


class SMSHandler(HandlerBase):
    def __init__(self, data: dict[str, str | None]) -> None:
        self.phone = data["phone"]
        super().__init__(data)

    def send(self) -> None:
        logger.info("SMS sent to {}. Data: {}", self.phone, self.data)


class EmailHandler(HandlerBase):
    def __init__(self, data: dict[str, str | None]) -> None:
        self.email = data["email"]
        super().__init__(data)

    def send(self) -> None:
        logger.info("Email sent to {}. Data: {}", self.email, self.data)


class PostHandler(HandlerBase):
    def __init__(self, data: dict[str, str | None]) -> None:
        self.url = data["url"]
        super().__init__(data)

    def send(self) -> None:
        logger.info("POST sent to {}. Data: {}", self.url, self.data)


SENDER_MAP: dict[EventTypes, type[HandlerBase]] = {
    EventTypes.SMS: SMSHandler,
    EventTypes.EMAIL: EmailHandler,
    EventTypes.POST: PostHandler,
}


def process_event(event: dict, db_session: "FakeDB") -> None:
    try:
        validated = EventSchema(**event)
        handler = SENDER_MAP[validated.event_type]
        serialized_payload = validated.model_dump()
        handler(serialized_payload).send()
        db_session.increase_processed()
    except (ValidationError, KeyError) as e:
        db_session.insert_failed(event, reason=str(e))
        return
