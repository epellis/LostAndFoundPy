# LostAndFound

## Installation
LostAndFound uses [Poetry](https://python-poetry.org) to manage and install dependencies.
```
poetry install
SLACK_TOKEN="XXX" poetry run uvicorn lostandfound.core:app --reload
```

## Development
When you are ready to commit code, please run the [Black](https://black.readthedocs.io/en/stable/installation_and_usage.html) formatter on your code:
```
black .
```
