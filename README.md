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
`SLACK_TOKEN="XXX" python main.py`

When you are ready to commit code, please run the 
[Black](https://black.readthedocs.io/en/stable/installation_and_usage.html) 
formatter on your code: `black .`

## Deployment
Key and deploy credentials are stored in a file called `app.yaml`. This stores
your Google App Engine configuration. Since it has private keys, it cannot
be added to version control. To deploy this app, you will need to put the
following in to the newly created file:
```
runtime: python37

env_variables:
    SLACK_TOKEN: "<REPLACE_ME>"
    LOGLEVEL: "DEBUG"
```

When you are ready to deploy the app to the cloud run: `gcloud app deploy`
