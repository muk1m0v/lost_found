from aiogram import Dispatcher, Bot
from aiogram.types import BotCommand
from mukimov.color import green
from services.db import *
from services.storage import DictStorage
from handler.handler import router
from states.state import router as state_router
from os import getenv
from dotenv import load_dotenv
import asyncio

load_dotenv()

bot = Bot(token=getenv('BOT_TOKEN'))
dp = Dispatcher(storage=DictStorage())

async def main():
    print(green('Bot Started!'))
    dp.include_router(router)
    dp.include_router(state_router)
    await init_tables()
    await bot.set_my_commands([
        BotCommand(command='start', description='запуск бота'),
        BotCommand(command='help', description='помощь'),
        BotCommand(command='add_item', description='добавить найденную вещь'),
        BotCommand(command='items', description='список доступных вещей'),
        BotCommand(command='item', description='карточка вещи'),
        BotCommand(command='my_claims', description='мои заявки'),
        BotCommand(command='claims', description='заявки на твою вещь'),
        BotCommand(command='cancel', description='отменить ввод')
    ])
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
