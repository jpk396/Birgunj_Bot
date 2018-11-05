#!/usr/bin/env python
from joinhider_bot import JoinhiderBot


def setup_arg_parser(parser):
    parser.add_argument('mode')
    parser.add_argument('chat_id', type=int)


def main(mode, chat_id, **kwargs):
    robot = JoinhiderBot() 
    robot.set_opts({'mode': mode})

    robot._init_bot(robot.get_token())
    res = robot.bot.leave_chat(chat_id)
