# Json Redo POC

## Assumptions AKA things you normally ask during refinement
1. No specific API requested, writing this as a CLI command.
2. I can't see any specific payload "data" in the provided json, assuming the data to send is the whole object.
3. If a field is not null, it will be validated even if optional
4. Some minimal level of data validation added on all fields that are not nullable (ex: url is an url, email is an email).
5. no data validation except it being a string added for phone number as this would depend on country, and system used.
6. Assumed manual check/discard required for failed events, storing them in a "database".

## Install
`poetry install`

## Running
- from outside venv `poetry run json-redo`
- from inside poetry shell `json-redo`
- from inside venv `python -m json_redo_interview.cli`


## Tests and Checks
from inside the virtualenv
- Code format: `ruff format .`
- Code lint: `ruff check .`
- Code Complexity: `xenon --no-assert -a A -m B -b B .`
- Keep code up to date: `refurb .`
- Type Hints: `mypy .`
- Tests: `pytest tests --cov json_redo_interview`


> **NB:** All these commands are run when executing `./checks.sh`
