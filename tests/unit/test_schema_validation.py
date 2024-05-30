from collections.abc import Callable

import pytest
from pydantic import ValidationError

from json_redo_interview.schemas import EventSchema


@pytest.mark.parametrize(
    ("type_name", "required_fields"),
    (
        pytest.param("sms", ["phone"], id="event type: SMS"),
        pytest.param("email", ["email"], id="event type: Email"),
        pytest.param("post", ["url"], id="event type: Post"),
    ),
)
def test_dynamically_required_fields(
    generate_event_payload: Callable[[dict], dict], type_name: str, required_fields: list[str]
) -> None:
    for field in required_fields:
        payload = generate_event_payload({"type": type_name, field: None})

        with pytest.raises(
            ValidationError, match=f"Value error, field '{field}' is required for {type_name} type events."
        ):
            EventSchema(**payload)
