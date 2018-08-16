import os

from tgram.webhook import build_wsgi_app

from joinhider_bot import JoinhiderBot

robot = JoinhiderBot() 
mode = os.environ['BOT_MODE']
robot.set_opts({'mode': mode})
app = build_wsgi_app(robot, workers=8)


if __name__ == '__main__':
    from bottle import run
    run(app)
