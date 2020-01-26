from fastapi import FastAPI
import os
import slack

app = FastAPI()
slack_token = os.environ["SLACK_TOKEN"]
slack_client = slack.WebClient(token=slack_token)


def get_channel_id_by_name(name: str) -> str:
    """ Returns a channel ID, or else raises a ValueError """
    channels = slack_client.api_call("channels.list").get("channels")
    for c in channels:
        if c["name"] == name:
            return c["id"]
    raise ValueError("Couldn't find channel ID")


@app.get("/")
def poll_notifications():
    try:
        channel_id = get_channel_id_by_name("slackbot-testing")
        # slack_client.chat_postMessage(channel=channel_id, text="Howdy Channel")
    except Exception as e:
        return {"success": False}
    return {"success": True}
