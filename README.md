# LostAndFound

## Installation
```
python3 -m venv env
source env/bin/activate
pip install  -r requirements.txt
```

## Development
This app exposes a small API endpoint under `/poll`. To run a server to test on,
run: `SLACK_TOKEN="XXX" python main.py`

When you are ready to commit code, please run the 
[Black](https://black.readthedocs.io/en/stable/installation_and_usage.html) 
formatter on your code: `black .`

## Deployment
Build the dockerfile with: `docker build . -t epellis/lostandfound`
You can run the image using `LOGLEVEL="INFO" SLACK_TOKEN="XXX" docker-compose up`

## Configuration
App configuration is stored in `config.toml`. 
[Toml](https://github.com/toml-lang/toml)
is a newer, more feature complete version of the `.ini` standard and provides
similar features to other formats like `.json`, and `.yaml`. Since the TOML
spec supports comments, the configuration file is self-documenting and should be
easy to extend. Since no keys are stored in this document, you are fine checking
it into version control.
