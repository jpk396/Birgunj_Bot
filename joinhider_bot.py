#!/usr/bin/env python
from pprint import pprint
from collections import Counter
import json
import logging
from argparse import ArgumentParser
from datetime import datetime, timedelta
import re

from telegram import ParseMode
from telegram.ext import CommandHandler, MessageHandler, Filters, RegexHandler
from tgram import TgramRobot, run_polling
from telegram import ParseMode

from database import connect_db

HELP = """*Join Hider Bot*

This bot removes messages about new user joined or left the chat.

*Commands*

/help - display this help message

*How to Use*

- Add bot as ADMIN to the chat group
- Allow bot to delete messages, any other admin permissions are not required

*Questions, Feedback*

Email: lorien@lorien.name

*Open Source*

The source code is available at [github.com/lorien/joinhider_bot](https://github.com/lorien/joinhider_bot)

*My Other Projects*

[@daysandbox_bot](https://t.me/daysandbox_bot) - bot that fights with spam messages in chat groups
[@nosticker_bot](https://t.me/nosticker_bot) - bot to delete stickers posted to group
[@coinsignal_robot](https://t.me/coinsignal_robot) - bot to be notified when price of specific coin reaches the level you have set, also you can use this bot just to see price of coins.
[@watchdog_robot](https://t.me/watchdog_robot) - bot to delete stickers, file attachments, links, photos, videos and many other types of messages
"""


class InvalidCommand(Exception):
    pass


class JoinhiderBot(TgramRobot):

    def before_start_processing(self):
        self.db = connect_db()

    def build_user_name(self, user):
        return user.username or ('#%d' % user.id)

    def handle_start_help(self, bot, update):
        msg = update.effective_message
        if msg.chat.type == 'private':
            bot.send_message(
                chat_id=msg.chat.id,
                text=HELP,
                parse_mode=ParseMode.MARKDOWN,
                disable_web_page_preview=True
            )

    def handle_new_chat_members(self, bot, update):
        msg = update.effective_message
        try:
            bot.delete_message(
                chat_id=msg.chat.id,
                message_id=msg.message_id,
            )
        except Exception as ex:
            if 'Message to delete not found' in str(ex):
                logging.error('Failed to delete msg: %s', ex)
                return
            elif "Message can't be deleted" in str(ex):
                logging.error('Failed to delete msg: %s', ex)
                return
            else:
                raise
        for user in msg.new_chat_members:
            self.db.chat.find_one_and_update(
                {'chat_id': msg.chat.id},
                {
                    '$set': {
                        'chat_username': msg.chat.username,
                        'active_date': datetime.utcnow(),
                    },
                    '$setOnInsert': {
                        'date': datetime.utcnow(),
                    },
                },
                upsert=True,
            )
            self.db.joined_user.find_one_and_update(
                {
                    'chat_id': msg.chat.id,
                    'user_id': user.id,
                },
                {'$set': {
                    'chat_username': msg.chat.username,
                    'user_username': user.username,
                    'date': datetime.utcnow(),
                }},
                upsert=True,
            )
            logging.debug('Removed join message for user %s at chat %d' % (
                self.build_user_name(user),
                msg.chat.id
            ))

    def handle_left_chat_member(self, bot, update):
        msg = update.effective_message
        try:
            bot.delete_message(
                chat_id=msg.chat.id,
                message_id=msg.message_id,
            )
        except Exception as ex:
            if 'Message to delete not found' in str(ex):
                logging.error('Failed to delete join message: %s' % ex)
                return
            elif "Message can't be deleted" in str(ex):
                logging.error('Failed to delete msg: %s', ex)
                return
            else:
                raise
        user = msg.left_chat_member
        self.db.chat.find_one_and_update(
            {'chat_id': msg.chat.id},
            {
                '$set': {
                    'chat_username': msg.chat.username,
                    'active_date': datetime.utcnow(),
                },
                '$setOnInsert': {
                    'date': datetime.utcnow(),
                },
            },
            upsert=True,
        )
        self.db.left_user.find_one_and_update(
            {
                'chat_id': msg.chat.id,
                'user_id': user.id,
            },
            {'$set': {
                'chat_username': msg.chat.username,
                'user_username': user.username,
                'date': datetime.utcnow(),
            }},
            upsert=True,
        )
        logging.debug('Removed left message for user %s at chat %d' % (
            self.build_user_name(user),
            msg.chat.id
        ))

    def register_handlers(self, dispatcher):
        dispatcher.add_handler(CommandHandler(
            ['start', 'help'], self.handle_start_help
        ))
        dispatcher.add_handler(MessageHandler(
            Filters.status_update.new_chat_members, self.handle_new_chat_members
        ))
        dispatcher.add_handler(MessageHandler(
            Filters.status_update.left_chat_member, self.handle_left_chat_member
        ))
        

if __name__ == '__main__':
    run_polling(JoinhiderBot)
