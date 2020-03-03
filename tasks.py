from celery import Celery

import bot

celery_app = Celery('tasks')
celery_app.conf.broker_url = 'redis://localhost:7002'


@celery_app.task
def set_avatar():
    me = bot.Bot()
    path_to_avatar = me.generate_random_avatar()
    bot.Bot().set_new_avatar(path_to_avatar)
