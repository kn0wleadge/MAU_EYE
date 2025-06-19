from aiogram import Bot, Dispatcher, F, types, Router
from aiogram.filters import Command
import os
import dotenv
from database.queries import add_user, get_user
import datetime
import logging
bot = Bot(os.getenv("TELEGRAM_BOT_TOKEN"))
dp = Dispatcher()
router = Router()
dp.include_router(router)

async def send_negative_publication_notification(publication, users):
    """Отправка уведомления о подозрительной публикации"""
    message = f"⚠️ Обнаружена подозрительная публикация:\n\n"
    message += f"📄 Текст: {publication.ptext[:500]}...\n\n"
    message += f"🔗 Ссылка: {publication.purl}\n"
    message += f"📅 Дата публикации: {publication.pdate}\n"
    message += f"👁 Просмотры: {publication.views}\n"
    message += f"❤️ Лайки: {publication.likes}\n"
    message += f"💬 Комментарии: {publication.comments}\n"
    message += f"↩️ Репосты: {publication.reposts}"
    for user in users:
        await bot.send_message(user.tg_id, message)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    #logger.info(f"User {message.from_user.id} started bot")
    if (await get_user(message.from_user.id) == None):
        await add_user(message.from_user.id,str(int(datetime.datetime.now().timestamp())))
        await message.answer("Бот мониторинга публикаций запущен. Я буду присылать уведомления о подозрительных публикациях.")
    else:
        await message.answer("Вы уже подписаны на рассылку :)")
async def run_bot():
    """Запуск бота и мониторинга"""
    await dp.start_polling(bot)

