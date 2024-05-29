import urllib.request

import ijson
import typer
from loguru import logger
from pydantic import ValidationError
from rich import print

from json_redo_interview.config import EVENT_SOURCE_FILE_URL
from json_redo_interview.handlers import route_event
from json_redo_interview.schemas import EventSchema

app = typer.Typer()


def main() -> None:
    with urllib.request.urlopen(EVENT_SOURCE_FILE_URL) as f:
        events = ijson.items(f, "item")
        count = 0
        for event in events:
            try:
                validated = EventSchema(**event)
            except ValidationError as e:
                logger.info("Validation error: {}", e)
            else:
                route_event(validated)

            count += 1

        print(f"Processed {count} events.")


if __name__ == "__main__":
    typer.run(main)
