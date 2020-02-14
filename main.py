import os
import slack
import ssl
from typing import List, Dict
import datetime
from enum import Enum
import logging
import toml
import dataclasses
from flask import Flask

# XXX: Asyncio cannot resolve SSL certs so we tell it to not bother
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE


app = Flask(__name__)
slack_token = os.environ["SLACK_TOKEN"]
slack_client = slack.WebClient(token=slack_token, ssl=ssl_context)

log_level = os.environ.get("LOGLEVEL", "WARNING").upper()
logging.basicConfig(level=log_level)

logging.info(f"Slack Token Present: {'' != os.environ['SLACK_TOKEN']}")


class Config:
    """ Config is a type safe interface between the running app and the provided
        configuration file, config.toml
    """

    @dataclasses.dataclass
    class Interval:
        """ Interval is a dataclass that stores the config in config.toml in
            a typed format that can easily be accessed
        """

        earliestDayBefore: datetime.timedelta
        latestDayAfter: datetime.timedelta
        message: str

        @classmethod
        def from_dict(cls, d: Dict):
            start = datetime.timedelta(days=d["earliestDayBefore"])
            end = datetime.timedelta(days=d["latestDayAfter"])
            return cls(start, end, d["message"])

    def __init__(self, config_file: str):
        self.toml = toml.load(config_file)
        self.intervals = [
            Config.Interval.from_dict(i[0]) for i in self.toml["intervals"].values()
        ]
        self.channel_name = self.toml["slack"]["channelName"]


class Message:
    class ContentType(Enum):
        UPLOAD = 1
        UNKNOWN = 2

    ts: datetime.datetime
    text: str
    content: ContentType

    def __init__(self, ts, text, content):
        self.ts = ts
        self.text = text
        self.content = content

    @classmethod
    def from_dict(cls, d: Dict):
        time = datetime.datetime.fromtimestamp(float(d["ts"]))
        if "upload" in d:
            return Message(time, d["text"], Message.ContentType.UPLOAD)
        else:
            return Message(time, d["text"], Message.ContentType.UNKNOWN)

    def __repr__(self) -> str:
        time = self.ts.strftime("%H:%M:%S")
        return f"Message(ts={time}, text={self.text})"


def get_channel_id_by_name(name: str) -> str:
    """ Returns a channel ID, or else raises a ValueError """
    channels = slack_client.channels_list(exclude_archived=1)["channels"]
    for c in channels:
        if c["name"] == name:
            return c["id"]
    raise ValueError("Couldn't find channel ID")


def get_channel_messages(channel_name: str) -> List[Message]:
    """ Returns all messages posted in a channel """
    channel_id = get_channel_id_by_name("slackbot-testing")
    messages = slack_client.channels_history(channel=channel_id)["messages"]
    return [Message.from_dict(m) for m in messages]


def filter_stale_messages(
    messages: List[Message], oldest: datetime.timedelta, youngest: datetime.timedelta
) -> List[Message]:
    """ Return a list of all messages posted that are younger than `age` """
    good_messages = []
    oldest_date = datetime.datetime.now() - oldest
    youngest_date = datetime.datetime.now() - youngest
    logging.debug(f"Looking for messages in {oldest_date} : {youngest_date}")
    for m in messages:
        if oldest_date < m.ts < youngest_date:
            good_messages.append(m)
    return good_messages


def filter_nonimage_messages(messages: List[Message]) -> List[Message]:
    """ Returns a list of all messages that are image posts """
    good_messages = []
    for m in messages:
        if m.content == Message.ContentType.UPLOAD:
            good_messages.append(m)
    return good_messages


def filter_reminder_messages(messages: List[Message]) -> List[Message]:
    """ Returns a list of all messsages that are not reminder posts """
    good_messages = []
    for m in messages:
        if "reminder" not in m.text.lower():
            good_messages.append(m)
    return good_messages


def create_reminder_text(original: str, addition: str) -> str:
    """ Returns the formatted reminder wording """
    return f"Reminder: {original}\n{addition}"


@app.route("/poll/")
def poll_notifications():
    config = Config("config.toml")
    logging.info(f"Loaded config with intervals: {config.intervals}")

    try:
        messages = get_channel_messages(config.channel_name)
        for interval in config.intervals:
            logging.info(
                f"Scanning: {interval.earliestDayBefore} to {interval.latestDayAfter}"
            )
            recent_messages = filter_stale_messages(
                messages, interval.earliestDayBefore, interval.latestDayAfter
            )
            logging.info(f"After Recent Filter: {len(recent_messages)} messages remain")
            images_messages = filter_nonimage_messages(recent_messages)
            logging.info(
                f"After Non image Filter: {len(images_messages)} messages remain"
            )
            original_messages = filter_reminder_messages(images_messages)
            logging.info(
                f"After Original Filter: {len(original_messages)} messages remain"
            )

            for m in original_messages:
                message = create_reminder_text(m.text, interval.message)
                logging.info(
                    f"Posting {message} at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                slack_client.chat_postMessage(
                    channel=get_channel_id_by_name("slackbot-testing"), text=message,
                )
                break

    except Exception as e:
        print(f"ERROR: Failed with exception: {e}")
        return {"success": False, "error": str(e)}
    return {"success": True}


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
