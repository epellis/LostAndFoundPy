# LostAndFound

## Prerequisite: Generating A Slack Token
TODO

## Development
You can install requirements and test locally using the following setup:
```
python3 -m venv env
source env/bin/activate
pip install  -r requirements.txt
```

This app exposes a small API endpoint under `/poll`. To run a server to test on,
run: `SLACK_TOKEN="XXX" python main.py`

When you are ready to commit code, please run the 
[Black](https://black.readthedocs.io/en/stable/installation_and_usage.html) 
formatter on your code: `black .`

## Deployment
Build the dockerfile with: `docker build . -t epelesis/lostandfound`

You can run the image using: `LOGLEVEL="INFO" SLACK_TOKEN="XXX" docker-compose up`

You can run the image as a daemon using: `LOGLEVEL="INFO" SLACK_TOKEN="XXX" docker-compose up -d`

If you ever need to clear everything and start over, run: `docker system prune -a`

## Uploading to Docker Hub
When you are done developing your app and ready to make a release you can
build it using the following commands. Replace `epelesis` with your [Docker Hub](https://hub.docker.com/)
account username. 

Build the dockerfile with: `docker build . -t epelesis/lostandfound`

Login to docker hub: `docker login`

Push image: `docker push epelesis/lostandfound`

Your image will now be publicly hosted on the Docker Hub!

## Configuration
App configuration is stored in `config.toml`. 
[Toml](https://github.com/toml-lang/toml)
is a newer, more feature complete version of the `.ini` standard and provides
similar features to other formats like `.json`, and `.yaml`. Since the TOML
spec supports comments, the configuration file is self-documenting and should be
easy to extend. Since no keys are stored in this document, you are fine checking
it into version control.

Cron configuration is in `entrypoint.sh`. This file is run as the last step
of `docker-compose up`. It writes a cron task to `wget` an endpoint every 24
hours and then launches the Python app. 
