import os
import string
import unittest

from bot import Bot, T_RGB
from main import load_envs


class BotFunctionsTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        load_envs()
        self.bot = Bot()

    def test_env(self):
        """ Проверка наличия всех необходимых переменных окружения """
        _vars = (
            'VK_LOGIN', 'VK_PASSWORD', 'VK_AVATAR_HEIGHT', 'VK_AVATAR_WIDTH'
        )
        for var in _vars:
            self.assertIsNotNone(
                os.getenv(var),
                msg=f'Не определена переменная окружения {var}'
            )

    def test_random_color(self):
        """ Проверка правильности генерации цветов """
        hex_symbols = string.hexdigits
        for _ in range(50_000):
            color: T_RGB = self.bot.get_random_color()
            with self.subTest(color=color):
                self.assertTrue(
                    isinstance(color, str),
                    msg='Цвет, возвращаемый из метода get_random_color должен быть строкой'
                )
                self.assertEqual(
                    len(color), 7,
                    msg='Цвет, возвращаемый из метода get_random_color должен быть длиной 7 символов'
                )
                self.assertTrue(
                    color.startswith('#'),
                    msg='Цвет, возвращаемый из метода get_random_color должен начинаться с символа "#"'
                )
                self.assertTrue(
                    all(list(map(lambda x: x in hex_symbols, color[1:]))),
                    msg='Цвет, возвращаемый из метода get_random_color'
                        f' должен содержать только символы "{string.hexdigits}" и ведущую "#"'
                )

    def test_generate_avatar(self):
        """ Проверка генерации рандомных аватаров """
        extensions = ('.png', '.jpg')

        for _ in range(100):
            path: str = self.bot.generate_random_avatar()
            full_path_without_suffix, suffix = os.path.splitext(path)
            full_path = full_path_without_suffix + suffix
            self.assertTrue(
                os.path.exists(full_path),
                msg=f'Картинки по этому пути ({full_path}) не существует'
            )
            self.assertIn(
                suffix, extensions,
                msg=f'У сгенерированной аватарки, должно быть расширение {"/".join(extensions)}'
            )
            os.remove(full_path)

    def test_singleton_bot(self):
        """ Проверка на то, соответствует ли бот паттерну Singleton """
        self.assertIs(
            Bot(), Bot(),
            msg='Бот не соответствует паттерну Singleton'
        )


