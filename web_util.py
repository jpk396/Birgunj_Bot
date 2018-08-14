#!/usr/bin/env python
import json
import logging
import uuid

import telebot
from bottle import request, abort

from joinhider_bot import init_bot_with_mode


def setup_web_app(app, mode):
    logging.basicConfig(level=logging.DEBUG)
    bot = init_bot_with_mode(mode)

    secret_key = str(uuid.uuid4())

    @app.route('/%s/' % secret_key, method='POST')
    def page():
        if request.headers.get('content-type') == 'application/json':
            json_string = request.body.read().decode('utf-8')
            update = telebot.types.Update.de_json(json_string)
            bot.process_new_updates([update])
            return ''
        else:
            abort(403)

    bot.remove_webhook()
    bot.set_webhook(url='https://telebot.grablab.org/joinhider_bot/%s/' % secret_key)
