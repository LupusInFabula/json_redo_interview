import json
from collections import Counter
from collections.abc import Callable, Iterator
from io import StringIO

from pytest_mock import MockerFixture

from json_redo_interview.cli import json_redo


def test_json_redo(
    mocker: MockerFixture,
    generate_events: Callable[[int], Iterator[dict]],
    generate_event_payload: Callable[[dict], dict],
) -> None:
    n_successes = 80
    events = list(generate_events(n_successes))
    expected_success_counter = Counter(event["type"] for event in events)

    # Add some failing events
    n_failures = 20
    for _ in range(n_failures):
        events.append(generate_event_payload({"type": "unknown"}))

    stream = StringIO(json.dumps(events))

    mocker.patch("json_redo_interview.cli.urlopen", return_value=stream)
    mock_print = mocker.patch("json_redo_interview.cli.print")

    mock_send_sms = mocker.patch("json_redo_interview.handlers.send_sms")
    mock_send_email = mocker.patch("json_redo_interview.handlers.send_email")
    mock_send_post = mocker.patch("json_redo_interview.handlers.send_post")
    json_redo()

    mock_print.assert_called_with(f"Successfully processed {n_successes} events, {n_failures} failed.")
    for type_name, n_events in expected_success_counter.items():
        match type_name:
            case "sms":
                assert mock_send_sms.call_count == n_events
            case "email":
                assert mock_send_email.call_count == n_events
            case "post":
                assert mock_send_post.call_count == n_events
            case _:
                raise ValueError(f"Unknown event type: {type_name}")
