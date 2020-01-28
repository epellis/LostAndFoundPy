from fastapi import FastAPI
import os
import slack
from typing import List, Dict
import time
import datetime

app = FastAPI()
slack_token = os.environ["SLACK_TOKEN"]
slack_client = slack.WebClient(token=slack_token)


class Message:
    ts: datetime.datetime
    text: str

    def __init__(self, ts, text):
        self.ts = ts
        self.text = text

    @classmethod
    def from_dict(cls, d: Dict):
        time = datetime.datetime.fromtimestamp(float(d["ts"]))
        return Message(time, d["text"])

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
    messages: List[Message], age: datetime.timedelta
) -> List[Message]:
    """ Return a list of all messages posted that are younger than `age` """
    good_messages = []
    for m in messages:
        if m.ts > datetime.datetime.now() - age:
            good_messages.append(m)
    return good_messages


@app.get("/poll/")
def poll_notifications():
    try:
        messages = get_channel_messages("slackbot-testing")
        recent_messages = filter_stale_messages(messages, datetime.timedelta(days=10))

        offset_m = int(os.environ["OFFSET_M"])

        for m in messages:
            if "Reminder" in m.text:
                continue

            post_time = max(m.ts, datetime.datetime.now()) + datetime.timedelta(
                minutes=offset_m
            )
            message = f"Reminder: {m.text}"
            print(f"Posting {message} at: {post_time.strftime('%Y-%m-%d %H:%M:%S')}")
            slack_client.chat_scheduleMessage(
                channel=get_channel_id_by_name("slackbot-testing"),
                post_at=str(post_time.timestamp()),
                text=message,
            )
            break

    except Exception as e:
        print(f"ERROR: Failed with exception: {e}")
        return {"success": False, "error": str(e)}
    return {"success": True}
