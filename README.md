# LostAndFound

## Installation
Pip and Pyenv track and manage requirements for this project.
```
python3 -m venv env
source env/bin/activate
pip install  -r requirements.txt
```

## Development
This app exposes a small API endpoint under `/poll`. To run a server, run:
`SLACK_TOKEN="XXX" python lostandfound/core.py`

When you are ready to commit code, please run the 
[Black](https://black.readthedocs.io/en/stable/installation_and_usage.html) 
formatter on your code: `black .`

## Deployment
When you are ready to deploy the app to the cloud run: `gcloud app deploy`
