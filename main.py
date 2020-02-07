import os
import slack
import ssl
from typing import List, Dict
import datetime
from enum import Enum
import logging
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

START_SEARCH = datetime.timedelta(days=14)
END_SEARCH = datetime.timedelta(days=13)

logging.info(f"Slack Token Present: {'' != os.environ['SLACK_TOKEN']}")


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
    for m in messages:
        if datetime.datetime.now() - oldest < m.ts < datetime.datetime.now() - youngest:
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


def create_reminder_text(original: str) -> str:
    """ Returns the formatted reminder wording """
    # TODO(Ned): date options so we can adjust when this runs
    return (
        f"Reminder: {original}\n*This item needs to be claimed or it will be removed*"
    )


@app.route("/poll/")
def poll_notifications():
    try:
        messages = get_channel_messages("slackbot-testing")
        recent_messages = filter_stale_messages(messages, START_SEARCH, END_SEARCH)
        images_messages = filter_nonimage_messages(recent_messages)
        original_messages = filter_reminder_messages(images_messages)

        for m in original_messages:
            # TODO(Ned): download file so we can reupload it
            message = create_reminder_text(m.text)
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
