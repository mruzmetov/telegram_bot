import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import config
from database.database import init_db
from handlers.start import router as start_router
from handlers.referral import router as referral_router
from handlers.buttons_handler import router as buttons_router   # Tugmalar uchun handler qo`shish


async def main() -> None:
    # Botni yaratish
    bot = Bot(
        token=config.BOT_TOKEN, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    # Dispatcher va Routerlarni qo‘shish
    dp = Dispatcher()
    dp.include_router(start_router)
    dp.include_router(referral_router)
    dp.include_router(buttons_router)

    # Ma'lumotlar bazasini ishga tushirish
    await init_db()

    logging.info("Bot has been started...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
