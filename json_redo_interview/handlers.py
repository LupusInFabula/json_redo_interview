from typing import TYPE_CHECKING, cast

from loguru import logger

from json_redo_interview.enums import EventTypes

if TYPE_CHECKING:
    from json_redo_interview.schemas import EventSchema


def send_sms(phone: str, data: dict) -> None:
    logger.info("SMS sent to {}. Data: {}", phone, data)


def send_email(email: str, data: dict) -> None:
    logger.info("Email sent to {}. Data: {}", email, data)


def send_post(url: str, data: dict) -> None:
    logger.info("POST sent to {}. Data: {}", url, data)


def route_event(event_model: "EventSchema") -> None:
    data = event_model.model_dump()
    if event_model.event_type == EventTypes.SMS:
        send_sms(cast(str, event_model.phone), data)

    elif event_model.event_type == EventTypes.EMAIL:
        send_email(cast(str, event_model.email), data)

    elif event_model.event_type == EventTypes.POST:
        send_post(cast(str, event_model.url), data)

    else:
        raise ValueError(f"Unknown event type: {event_model.event_type}")
