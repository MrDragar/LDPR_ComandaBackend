import logging
import random
from vkbottle import Keyboard, Text, VKApps, Bot
from aiogram import Bot as TgBot
from maxapi import Bot as MaxBot
from aiogram.types import WebAppInfo
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from maxapi.types import MessageButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder
from src.domain.entities import Sources
from src.services.interfaces import INotificationService

logger = logging.getLogger(__name__)
WEBAPP_URL = "https://миниапп.командалдпр.рф/app"


class NotificationService(INotificationService):
    def __init__(self, vk_bot: Bot, tg_bot: TgBot, max_bot: MaxBot):
        self.vk_bot = vk_bot
        self.tg_bot = tg_bot
        self.max_bot = max_bot

    async def notify_user_vk(self, peer_id: int, text: str, keyboard=None) -> None:
        try:
            kwargs = {"peer_id": peer_id, "message": text, "random_id": 0}
            if keyboard:
                kwargs["keyboard"] = keyboard
            await self.vk_bot.api.messages.send(**kwargs)
            logger.info(f"VK notification sent to {peer_id}")
        except Exception as e:
            logger.error(f"Failed to send VK notification to {peer_id}: {e}")

    async def notify_user_tg(self, chat_id: int, text: str) -> None:
        try:
            await self.tg_bot.send_message(chat_id=chat_id, text=text)
            logger.info(f"TG notification sent to {chat_id}")
        except Exception as e:
            logger.error(f"Failed to send TG notification to {chat_id}: {e}")

    async def notify_user_max(self, user_id: int, text: str) -> None:
        try:
            await self.max_bot.send_message(user_id=user_id, text=text)
            logger.info(f"MAX notification sent to {user_id}")
        except Exception as e:
            logger.error(f"Failed to send MAX notification to {user_id}: {e}")

    async def notify_user(self, user_id: int, source: Sources, text: str) -> None:
        """Общий метод для отправки уведомлений во все поддерживаемые источники."""
        if source == Sources.VK:
            await self.notify_user_vk(user_id, text)
        elif source == Sources.TG:
            await self.notify_user_tg(user_id, text)
        elif source == Sources.MAX:
            await self.notify_user_max(user_id, text)
        else:
            logger.error(f"Unknown source: {source}")

    async def send_menu(self, chat_id: int, source: Sources) -> None:
        """Отправляет меню с клавиатурой пользователю в зависимости от источника."""
        try:
            if source == Sources.VK:
                await self._send_vk_menu(chat_id)
            elif source == Sources.TG:
                await self._send_tg_menu(chat_id)
            elif source == Sources.MAX:
                await self._send_max_menu(chat_id)
            else:
                logger.error(f"Unknown source for menu: {source}")
        except Exception as e:
            logger.error(f"Failed to send menu to {chat_id} via {source}: {e}")

    async def _send_vk_menu(self, peer_id: int) -> None:
        """Отправляет меню для VK."""
        kb = Keyboard(one_time=False)
        vk_app = VKApps(app_id=54510502, owner_id=200072379, label="Открыть приложение")

        kb.add(vk_app).row()
        kb.add(Text("Поручения штаба", payload=f"{random.randint(0, 1000000)}"))
        kb.add(Text("Действующие поручения")).row()
        kb.add(Text("Личный кабинет"))
        kb.add(Text("Реферальная ссылка")).row()
        kb.add(Text("Обучение"))
        kb.add(Text("Закрытые мероприятия")).row()

        keyboard_json = kb.get_json()
        await self.notify_user_vk(peer_id, "Меню:", keyboard=keyboard_json)

    async def _send_tg_menu(self, chat_id: int) -> None:
        """Отправляет меню для Telegram."""
        web_app_info = WebAppInfo(url=WEBAPP_URL)
        builder = ReplyKeyboardBuilder()

        builder.button(text="Открыть приложение", web_app=web_app_info)
        builder.button(text="Поручения штаба")
        builder.button(text="Действующие поручения")
        builder.button(text="Личный кабинет")
        builder.button(text="Реферальная ссылка")
        builder.button(text="Обучение")
        builder.button(text="Закрытые мероприятия")
        builder.adjust(1, 2, 2, 1, 1)

        keyboard = builder.as_markup(resize_keyboard=True)
        await self.tg_bot.send_message(chat_id=chat_id, text="Меню:", reply_markup=keyboard)
        logger.info(f"TG menu sent to {chat_id}")

    async def _send_max_menu(self, user_id: int) -> None:
        """Отправляет меню для MAX."""
        builder = InlineKeyboardBuilder()

        builder.row(MessageButton(text="Поручения штаба"))
        builder.row(MessageButton(text="Действующие поручения"))
        builder.row(MessageButton(text="Личный кабинет"))
        builder.row(MessageButton(text="Обучение"), MessageButton(text="Реферальная ссылка"))
        builder.row(MessageButton(text="Закрытые мероприятия"))

        keyboard = builder.as_markup()
        await self.max_bot.send_message(user_id=user_id, text="Меню:", attachments=[keyboard])
        logger.info(f"MAX menu sent to {user_id}")
