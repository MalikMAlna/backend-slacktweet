#!/usr/bin/env python3
"""
A standalone Slack client implementation
see https://slack.dev/python-slackclient/
"""

import os
from slack.web.client import WebClient
from slack.errors import SlackApiError
from dotenv import load_dotenv

load_dotenv()

bot_user_token = os.environ["BOT_USER_TOKEN"]
client = WebClient(token=bot_user_token)
try:
    response = client.chat_postMessage(
        channel="bot-safehouse",
        text=":tada: How may I serve you master?"
    )
except SlackApiError as e:
    # You will get a SlackApiError if "ok" is False
    assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'


# class SlackClient:
#     pass


# def main():
#     pass


# if __name__ == '__main__':
#     main()
