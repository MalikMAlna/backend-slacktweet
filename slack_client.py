#!/usr/bin/env python3
"""
A standalone Slack client implementation
see https://slack.dev/python-slackclient/
"""

import os
import sys
from slack.rtm.client import RTMClient
from slack.web.client import WebClient
from dotenv import load_dotenv
import logging.config
import logging
import yaml

load_dotenv()

# Guard against unsupported/older versions of Python
if sys.version_info[0] < 3 and sys.version_info[1] < 7:
    raise RuntimeError("Please use Python 3.7+")

BOT_NAME = "al-raasid"


# Create module logger from config file
def config_logger():
    """Setup logging configuration"""
    with open('logging.yaml') as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    return logging.getLogger(__name__)


logger = config_logger()


class SlackClient:
    def __init__(self, bot_user_token, bot_id=None):
        self.name = BOT_NAME
        self.bot_id = bot_id
        if not self.bot_id:
            # Read the bot's id by calling auth.test
            response = WebClient(token=bot_user_token).api_call('auth.test')
            self.bot_id = response['user_id']
            logger.info(f"My bot_id is {self.bot_id}")

        self.sc = RTMClient(token=bot_user_token, run_async=True)

        # Connect our callback events to the RTM client
        RTMClient.run_on(event="hello")(self.on_hello)
        RTMClient.run_on(event="message")(self.on_message)
        RTMClient.run_on(event="goodbye")(self.on_goodbye)

        # startup our client event loop
        self.future = self.sc.start()
        self.at_bot = f'<@{self.bot_id}>'
        logger.info("Created new SlackClient Instance")

    def __repr__(self):
        return self.at_bot

    def __str__(self):
        return self.__repr__()

    def on_hello(self, **payload):
        """Slack is confirming our connection request"""
        logger.info(f"{self} is connected to Slack's RTM server")
        self.post_message(f"{self.name} is now online")

    def on_message(self, **payload):
        data = payload["data"]
        logger.info(data['text'])

    def on_goodbye(self, **payload):
        pass

    def post_message(self, msg_text, channel=BOT_CHAN):
        pass

    def run(self):
        logger.info("Waiting for things to happen...")
        loop = self.future.get_loop()
        # Forever Waiting...
        loop.run_until_complete(self.future)
        logger.info("Things are now done happening.")


def main(args):
    slackclient = SlackClient(
        os.environ['BOT_USER_TOKEN'], os.environ['BOT_USER_ID'])
    slackclient.run()


if __name__ == '__main__':
    main(sys.argv[1:])
    logger.info("Program Completed.")


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
