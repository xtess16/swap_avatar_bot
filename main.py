import os
from dotenv import load_dotenv

import bot


def load_envs():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)


def main():
    load_envs()
    me = bot.Bot()
    me.start()


if __name__ == '__main__':
    main()
