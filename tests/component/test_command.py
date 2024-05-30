import json
from collections import Counter
from collections.abc import Callable, Iterator
from io import BytesIO

from pytest_mock import MockerFixture

from json_redo_interview.cli import json_redo
from json_redo_interview.handlers import EmailHandler, PostHandler, SMSHandler


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

    stream = BytesIO(json.dumps(events, indent=4).encode("utf-8"))

    mocker.patch("json_redo_interview.cli.urlopen", return_value=stream)
    mock_print = mocker.patch("json_redo_interview.cli.print")

    mock_send_sms = mocker.patch.object(SMSHandler, "send")
    mock_send_email = mocker.patch.object(EmailHandler, "send")
    mock_send_post = mocker.patch.object(PostHandler, "send")
    json_redo()

    mock_print.assert_called_with(f"Processed {n_successes + n_failures} events, {n_failures} failed.")
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
