from collections.abc import Callable, Iterator
from random import choice

import pytest
from faker import Faker

faker = Faker()


@pytest.fixture(scope="module")
def generate_event_payload() -> Callable[[dict], dict]:
    """
    Generates a payload for an event as follows.
    ```python
    {
        "name": faker.name(),
        "email": faker.email(),
        "phone": faker.phone_number(),
        "url": faker.url(),
        "type": choice(supported_types),
    }
    ```

    Any value can be overridden by passing a dictionary to the function with the desired key-value pair.

    Example fixture usage:
    ```python
    def test_sample_test(generate_event_payload):
        event = generate_event_payload({"type": "sms", "email": None})
    ```
    """
    supported_types = ["sms", "email", "post"]

    def _generate_payload(override: dict) -> dict:
        payload = {
            "name": faker.name(),
            "email": faker.email(),
            "phone": faker.phone_number(),
            "url": faker.url(),
            "type": choice(supported_types),
        }
        return payload | override

    return _generate_payload


@pytest.fixture(scope="function")
def generate_events(
    generate_event_payload: Callable[[dict], dict],
) -> Callable[[int], Iterator[dict]]:
    """
    Generates the requested number of events (default 10) and returns them as an Iterator.
    """

    def _generator(n_events: int = 10) -> Iterator[dict]:
        for _ in range(n_events):
            yield generate_event_payload({})

    return _generator
