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
        time = datetime.datetime.utcfromtimestamp(float(d["ts"]))
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


@app.get("/")
def poll_notifications():
    try:
        messages = get_channel_messages("slackbot-testing")
        print("History", *messages, sep="\n")
    except Exception as e:
        return {"success": False, "error": str(e)}
    return {"success": True}

