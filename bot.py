import datetime
import os
import random
import string
import time
from typing import NoReturn

import requests
import vk_api
from PIL import Image

import tasks

# Тип - RGB цвет в формате #xxxxxx
T_RGB = str


class MetaSingleton(type):
    """ Реализация паттерна Singleton через метакласс """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Bot(metaclass=MetaSingleton):
    def __init__(self):
        self.vk_session = vk_api.VkApi(os.getenv('VK_LOGIN'), os.getenv('VK_PASSWORD'))

    def auth(self) -> bool:
        """ Авторизовывает бота в ВК """
        try:
            self.vk_session.auth()
        except vk_api.exceptions.BadPassword:
            print('Неверный логин или пароль')
            return False
        except vk_api.exceptions.LoginRequired:
            print('Не указан логин или пароль')
            return False
        else:
            return True

    def start(self) -> NoReturn:
        self.auth()
        # tasks.set_avatar.delay()
        tasks.set_avatar()

    def get_random_color(self) -> T_RGB:
        """
            Создает рандомный цвет
        :return: Цвет в формате #xxxxxx (rgb)
        """
        color: T_RGB = '#'
        hex_symbols = string.digits + 'abcdef'

        for _ in range(6):
            color += random.choice(hex_symbols)

        return color

    def generate_random_avatar(self) -> str:
        """
            Генерирует и сохраняет рандомную аватарку
        :return: Путь к аватарке
        """
        width = int(os.getenv('VK_AVATAR_WIDTH'))
        height = int(os.getenv('VK_AVATAR_HEIGHT'))
        # Создаем картинку из параметров, полученных из переменных окружения
        # и заливаем её рандомным цветом
        image = Image.new('RGB', (width, height), self.get_random_color())
        path_to_image = os.path.join('./avatars', datetime.datetime.now().strftime('%d_%B_%Y__%H_%M_%S')+'.png')
        if not os.path.exists('./avatars'):
            os.mkdir('./avatars')
        image.save(path_to_image)
        return os.path.abspath(path_to_image)

    def set_new_avatar(self, path) -> NoReturn:
        """
            Обновление аватарки на странице
        :param path: Путь к аватарке на пк
        """
        # Получаем url для загрузки аватарки
        if (upload_url := self.vk_session.method('photos.getOwnerPhotoUploadServer').get('upload_url')) is not None:
            # Пересылаем картинку на полученный url
            with open(path, 'rb') as photo:
                response = requests.post(upload_url, files={'file': photo})
            # Если загрузка картинки на сервер была успешной
            if response.status_code == 200:
                # Делаем нашу картинку аватаркой страницы
                self.vk_session.method('photos.saveOwnerPhoto', {
                    'server': response.json()['server'],
                    'hash': response.json()['hash'],
                    'photo': response.json()['photo']
                })

                # Получаем список последних 5 записей на стене, для того
                # чтобы найти пост с информацией об обновлении фотографии на странице
                posts = self.vk_session.method('wall.get', {
                    'owner_id': '329164718',
                    'filter': 'owner',
                    'count': 5
                })

                # Удаляем пост с информацией об обновлении фотографии на странице
                for post in posts['items']:
                    how_long_ago = datetime.datetime.now() - datetime.datetime.fromtimestamp(post['date'])
                    if how_long_ago.total_seconds() > 600:
                        break
                    if post['post_source']['data'] == 'profile_photo':
                        self.vk_session.method('wall.delete', {
                            'post_id': post['id']
                        })
                        break
