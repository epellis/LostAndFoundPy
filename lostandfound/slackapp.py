from abc import ABC, abstractmethod

# TODO: Compose, do not inherit


class Config:
    """ Stores loaded config.toml file """

    def __init__(self, file: str):
        pass


class SlackApp(ABC):
    """ Abstract Slack App Class. Your class should inherit from this one so
        that you can use the predefined methods.
    """

    def __init__(self, token: str, config_toml: str):
        self.token = token
        self.config = Config(config_toml)

    @abstractmethod
    def post_text_message(self, channel: str, contents: str):
        """ Post a message with the given text to a channel """
