#!/usr/bin/env python3
"""
A standalone Slack client implementation
see https://slack.dev/python-slackclient/
"""

import os
import sys
from slack.web.client import WebClient
from slack.rtm.client import RTMClient
from dotenv import load_dotenv
import logging.config as logcon
from logging import getLogger
import yaml

load_dotenv()

# Guard against unsupported/older versions of Python
if sys.version_info[:3] < 3.5:
    raise RuntimeError("Please use Python 3.5+")

BOT_NAME = "al-raasid"

# Create module logger from config file


def config_logger():
    """Setup logging configuration"""
    with open('logging.yaml') as f:
        config = yaml.safe_load(f.read())
        logcon.dictConfig(config)
    return getLogger(__name__)


logger = config_logger()


class SlackClient:
    def __init__(self, bot_user_token, bot_id=None):
        self.name = BOT_NAME
        self.bot_id = bot_id
        if not self.bot_id:
            # Read the bot's id by calling auth.test
            response = WebClient(token=bot_user_token).api_call('auth.test')
            self.bot_id = response['user_id']
            print(f"My bot_id is {self.bot_id}")

        self.sc = RTMClient(token=bot_user_token, run_async=True)

        # Connect our callback events to the RTM client
        RTMClient.run_on(event="hello")(self.on_hello)
        RTMClient.run_on(event="message")(self.on_message)
        RTMClient.run_on(event="goodbye")(self.on_goodbye)

        # startup our client event loop
        self.future = self.sc.start()
        self.at_bot = f'<@{self.bot_id}>'
        print("Created new SlackClient Instance")

    def on_hello(self, **payload):
        data = payload["data"]
        print(data)

    def on_message(self, **payload):
        data = payload["data"]
        print(data['text'])

    def on_goodbye(self, **payload):
        pass

    def run(self):
        print("Waiting for things to happen...")
        loop = self.future.get_loop()
        # Forever Waiting...
        loop.run_until_complete(self.future)
        print("Things are now done happening.")


def main(args):
    slackclient = SlackClient(
        os.environ['BOT_USER_TOKEN'], os.environ['BOT_USER_ID'])
    slackclient.run()


if __name__ == '__main__':
    main(sys.argv[1:])
    print("Program Completed.")


# bot_user_token = os.environ["BOT_USER_TOKEN"]
# client = WebClient(token=bot_user_token)
# try:
#     response = client.chat_postMessage(
#         channel="bot-safehouse",
#         text=":tada: How may I serve you master?"
#     )
# except SlackApiError as e:
#     # You will get a SlackApiError if "ok" is False
#     assert e.response["error"]  # str like 'invalid_auth',
# 'channel_not_found'
