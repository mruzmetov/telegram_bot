from aiogram import types, Router
from aiogram.filters import Command
from database.database import SessionLocal, User
from sqlalchemy.future import select

router = Router()

@router.message(Command("start"))
async def referral_command(message: types.Message):

    args = message.text.split()  
    referral_id = message.text.split(" ")[1] if len(args) > 1 else None

    async with SessionLocal() as db:
        # Agar referrar id bo`lsa taklif qilgan odamni topamiz
        if referral_id:
            result = await db.execute(select(User).filter(User.telegram_id == int(referral_id)))
            inviter = result.scalars().first()
        else:
            inviter = None

        # Yangi foydalanuvchini bazaga qo`shamiz`
        result = await db.execute(select(User).filter(User.telegram_id == message.from_user.id))
        user = result.scalars().first()

        if not user:
            new_user = User(
                telegram_id = message.from_user.id,
                first_name = message.from_user.first_name,  # Ism
                last_name = message.from_user.last_name,    # Familiya
                username = message.from_user.username,
                referral_code = str(message.from_user.id),
                balance = 0,
                invited_by = int(referral_id) if referral_id else None
            )
            db.add(new_user)
            await db.commit()

            #Agar referral orqali qo`shilgan bo`lsa, taklif qiluvchiga 5000 so`m qo`shamiz
            if inviter and inviter.telegram_id != message.from_user.id:
                # inviter.balance borligini tekshiramiz, agar None bo`lsa, 0 qilib qo`yamiz
                if inviter.balance is None:
                    inviter.balance = 0
                
                inviter.balance += 5000
                await db.commit()

                #taklif qilgan foydalanuvchiga xabar yuborish
                try:
                    await message.bot.send_message(
                        chat_id = inviter.telegram_id,
                        text = f"🎉 Siz {message.from_user.username} ni taklif qildingiz va 5000 so‘m mukofot oldingiz!"
                    )
                    print(f"✅{inviter.username} ga 5000 so`m qo'shildi va xabar yuborildi")
                except Exception as e:
                    print(f"❌ Xabar yuborishda xatolik: {e}")
                
                

        await message.answer("Xush kelibsiz! Siz tizimga muvaffaqiyatli qo‘shildingiz ✅")