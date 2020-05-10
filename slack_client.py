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
import shlex

load_dotenv()

# Guard against unsupported/older versions of Python
if sys.version_info[0] < 3 and sys.version_info[1] < 7:
    raise RuntimeError("Please use Python 3.7+")

# Globals
BOT_NAME = "al-raasid"
BOT_CHAN = "bot-safehouse"
bot_commands = {
    'help':  'Shows this helpful command reference.',
    'ping':  'Show uptime of this bot.',
    'exit':  'Shutdown the entire bot (requires app restart)',
    'quit':  'Same as exit.',
    'list':  'List current twitter filters and their counters',
    'add':  'Add some twitter keyword filters.',
    'del':  'Remove some twitter keyword filters.',
    'clear':  'Remove all twitter filters',
    'raise':  'Manually test exception handler'
}


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

    # Callback Methods
    def on_message(self, **payload):
        """Slack has sent the bot a message"""
        data = payload["data"]
        if "text" in data and self.at_bot in data['text']:
            # parse everything after <@Bot> mention
            raw_cmd = data["text"].split(self.at_bot)[1].strip().lower()
            chan = data['channel']
            # handling cmd
            response = self.handle_command(raw_cmd, chan)
            self.post_message(response, chan)

    def handle_command(self, raw_cmd, chan):
        "Parses a raw_cmd string directed at the bot"
    #     return "To crush your enemies, to see them driven before you,"
    # + "and to hear the lamentations of their people!"
        response = None
        args = shlex.split(raw_cmd)
        cmd = args[0].lower()
        logger.info(f'{self} received command: "{raw_cmd}"')
        if cmd not in bot_commands:
            response = f'Unknown Command: "{cmd}"'
            logger.error(f'{self} {response}')
        # Now there is a valid command that must be processed
        elif cmd == 'help':
            pass
        elif cmd == 'ping':
            pass
        elif cmd == 'list':
            pass
        return response

    def on_goodbye(self, **payload):
        logger.warning(f"{self} is disconnecting now")

    def post_message(self, msg_text, channel=BOT_CHAN):
        """Sends a message to a Slack channel"""
        assert self.sc._web_client is not None
        if msg_text:
            self.sc._web_client.chat_postMessage(
                channel=channel,
                text=msg_text
            )

    # Waiting for something method
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
