# Json Redo POC

## Assumptions AKA things you normally ask during refinement
1. No specific API requested, writing this as a CLI command.
2. I can't see any specific payload "data" in the provided json, assuming the data part is the whole object.
3. If a field is not null, it will be validated even if optional

## Install
`poetry install`

## Running
- from outside venv `poetry run json-redo`
- from inside poetry shell `json-redo`
- from inside venv `python -m json_redo_interview.cli`


## Tests and Checks
from inside the virtualenv
- Tests: `pytest tests`
- Code format: `ruff format .`
- Code lint: `ruff check .`
- Code Complexity: `xenon --no-assert -a A -m B -b B .`
- Type Hints: `mypy .`
- Code best practices: `refurb .`

All these commands are run when executing `./checks.sh`
