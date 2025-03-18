import os
import sys
from aiogram import types, Router
from aiogram.filters import CommandStart
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database.database import SessionLocal, User
from sqlalchemy.future import select
from keyboard import main_menu, admin_menu
import config

router = Router()

@router.message(CommandStart())
async def start_command(message: types.Message):
    async with SessionLocal() as db:
        result = await db.execute(select(User).filter(User.telegram_id == message.from_user.id))
        user = result.scalars().first()

        if not user:
            new_user = User(
                telegram_id=message.from_user.id,
                first_name=message.from_user.first_name,  # Ism
                last_name=message.from_user.last_name,    # Familiya
                username=message.from_user.username,      # Username
                referral_code=str(message.from_user.id)
            )
            db.add(new_user)
            await db.commit()
            await message.answer("Xush kelibsiz! Siz tizimga muvaffaqiyatli qo‘shildingiz ✅", reply_markup=main_menu)
        else:
            await message.answer("Asosiy menu", reply_markup=main_menu)
