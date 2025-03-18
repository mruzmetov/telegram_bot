import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))  # Asosiy katalogga yo‘l qo‘shish
from database.database import SessionLocal, User
import asyncio
from keyboard import vote_buttons,  get_balance_buttons, get_cards_buttons, back_button, main_menu, admin_menu

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from aiogram import types, Router, F
from database.database import SessionLocal, User
from sqlalchemy.future import select
import config
from keyboard import get_referral_button, back_button_and_vote
from utils.utils import get_time_left



router = Router()

#Telefon raqamni so`rash`
@router.message(F.text == "🗣 Ovoz berish")
async def vote_handler(message: types.Message):
    await message.answer("Ovoz berish uchun 📞 Telefon raqamingizni yuboring. \n\n"
                         "<b>(+998901234567</b> yoki <b>901234567</b> formatida kiriting)", 
                         reply_markup=back_button,
                         parse_mode="HTML")

#Telefon raqamni qabul qilish va saqlash
@router.message(F.text.regexp(r"^\+?\d{9,15}$"))  # Telefon raqami formati
async def save_phone_number(message: types.Message):
    phone_number = message.text.strip()

    async with SessionLocal() as db:
        result = await db.execute(select(User).filter(User.telegram_id == message.from_user.id))
        user = result.scalars().first()

        if user:
            user.phone_number = phone_number
            await db.commit()

            waiting_msg = await message.answer("Iltimos kuting👀👀...")
            await asyncio.sleep(3)
            await message.bot.delete_message(chat_id=message.chat.id, message_id=waiting_msg.message_id)

            error_msg = await message.answer(
                "<b>Xozircha avtomatik ovoz berib bo‘lmayabdi, pastdagi havola yordamida ovoz berib pul ishlashinigiz mumkin!👇👇👇</b>",
                reply_markup=vote_buttons(message.from_user.id),
                parse_mode="HTML"
            )
            
            if(error_msg):
                await message.answer(
                    "👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆👆",
                    reply_markup=back_button_and_vote
                )

        else:
            await message.answer("❌ Siz avval /start buyrug‘ini yuborishingiz kerak.")

        

# ✅ Ovoz berganini tasdiqlash
@router.message(lambda message: message.text == "✅ Ovoz berdim")
async def vote_confirm_handler(message: types.Message):
    async with SessionLocal() as db:
        result = await db.execute(select(User).filter(User.telegram_id == message.from_user.id))
        user = result.scalars().first()

        if user:
            user.vote += 1
            await db.commit()
            await message.answer("⏳ Sizning bergan ovozingiz <b>operator</b>ga yuborildi. \n"
                                 "Jarayon natijasini 5-15 daqiqa ichidada javobini olasiz!", 
                                 reply_markup=back_button,
                                 parse_mode="HTML")
        else:
            await message.answer("❌ Siz avval /start buyrug‘ini yuborishingiz kerak.")



@router.message(lambda message: message.text == "💰 Balans")
async def balance_handler(message: types.Message):
    async with SessionLocal() as db:
        result = await db.execute(select(User).filter(User.telegram_id == message.from_user.id))
        user = result.scalars().first()

        if user and user.balance is not None:
            balance = user.balance
        else:
            balance = 0  # Agar foydalanuvchi yo‘q bo‘lsa yoki balance yo‘q bo‘lsa

        #Foydalanuvchining kartasi bor yo`qligini tekshirish`
        has_card = user.card_number is not None if user else False

        await message.answer(
            f"💰 Sizning balansingiz: <b>{balance} so‘m</b>\n\nPul yechish yoki karta qo‘shish uchun pastdagi tugmalardan foydalaning.",
            parse_mode="HTML",
            reply_markup=get_balance_buttons(has_card)
        )


@router.callback_query(lambda call: call.data == "withdraw_money")
async def withdraw_money(call: types.CallbackQuery):
    async with SessionLocal() as db:
        result = await db.execute(select(User).filter(User.telegram_id == call.from_user.id))
        user = result.scalars().first()

        if not user or user.balance is None:
            await call.message.answer("❌ Sizning balansingiz mavjud emas yoki tizimda ro'yxatdan o'tmagansiz!")
            return

        # Foydalanuvchidan summa so'rash
        await call.message.answer("💳 Qancha pul yechmoqchisiz? (Masalan: 75000 yoki 100000)")
        
        # Foydalanuvchi javobini kutish
        @router.message(F.text.regexp(r"^\d+$"))  # Faqat raqamlar qabul qilinadi
        async def process_withdraw_amount(message: types.Message):
            try:
                amount = int(message.text)  # Foydalanuvchi yuborgan summani raqamga aylantirish
            except ValueError:
                await message.answer("❌ Noto'g'ri format! Faqat raqam kiriting (masalan: 75000).")
                return

            # Summani tekshirish
            if amount < 75000:
                await message.answer("❌ Pulni yechish uchun kamida <b>75 000 so‘m</b> bo'lishi kerak!", parse_mode="HTML")
                return

            if user.balance < amount:
                await message.answer(f"❌ Sizning balansingizda yetarli mablag' yo'q. Balansingiz: <b>{user.balance} so'm</b>", parse_mode="HTML")
                return

            # Agar karta raqami mavjud bo'lmasa
            if not user.card_number:
                await message.answer("❌ Avval karta raqamingizni qo'shishingiz kerak!", reply_markup=get_balance_buttons(False))
                return

            # Balansdan summani yechish
            user.balance -= amount
            await db.commit()

            await message.answer(f"<b><i>✅ {amount} so‘m</i></b> muvaffaqiyatli yechildi! \nTo'lov jarayoni operator javobini kuting...", parse_mode="HTML")

@router.callback_query(lambda call: call.data == "add_card")
async def add_card_handler(call: types.CallbackQuery):
    await call.message.answer("<b>UzCard/Humo</b> Iltimos karta raqamingizni yozib yuboring:", parse_mode="HTML")

#Karta raqamni qabul qilish va saqlash jarayoni
@router.message(F.text.regexp(r"^\d{16}$"))
async def save_card_number(message: types.Message):
    card_number = message.text.strip()

    async with SessionLocal() as db:
        result = await db.execute(select(User).filter(User.telegram_id == message.from_user.id))
        user = result.scalars().first()

        if user:
            user.card_number = card_number
            await db.commit()
            await message.answer("✅ Karta raqamingiz muvaffaqiyatli saqlandi!")
        else:
            await message.answer("❌ Siz avval /start buyrug‘ini yuborishingiz kerak.")


@router.message(lambda message: message.text == "💳Kartalarim")
async def show_cards_handler(message: types.Message):
    async with SessionLocal() as db:
        result = await db.execute(select(User).filter(User.telegram_id == message.from_user.id))
        user = result.scalars().first()

        if user and user.card_number:
            # Karta raqamini formatda ko'rsatish (8600 **** 5496)
            card_number = user.card_number
            masked_card = f"{card_number[:4]} **** {card_number[-4:]}"
            await message.answer(
                f"💳 Sizning kartangiz: <b>{masked_card}</b>",
                parse_mode="HTML",
                reply_markup=get_cards_buttons()  # "Yana karta qo'shish" va "O'chirish" tugmalari
            )
        else:
            await message.answer(
                "❌ Sizda hech qanday karta raqami qo'shilmagan.",
                reply_markup=get_cards_buttons()  # "Yana karta qo'shish" tugmasi
            )



@router.message(lambda message: message.text == "⬅️ Orqaga")
async def back_to_main_menu(message: types.Message):
    await message.answer("Asosiy menyuga qaytingiz.", reply_markup=main_menu)

@router.callback_query(lambda call: call.data == "delete_card")
async def delete_card_handler(call: types.CallbackQuery):
    async with SessionLocal() as db:
        result = await db.execute(select(User).filter(User.telegram_id == call.from_user.id))
        user = result.scalars().first()

        if user and user.card_number:
            user.card_number = None  # Karta raqamini o'chirish
            await db.commit()
            await call.message.answer("✅ Karta raqamingiz muvaffaqiyatli o'chirildi!")
        else:
            await call.message.answer("❌ Sizda hech qanday karta raqami qo'shilmagan.")


@router.message(lambda message: message.text == "👥 Do‘stlar taklif qilish")
async def invite_friends_handler(message: types.Message):
    referral_button = get_referral_button(config.BOT_NAME, message.from_user.id)

    # Rasm yuklash
    photo_url = "https://daryo.uz/cache/2021/11/1-168-1280x853.jpg"  # Rasm URL'sini o'zgartiring!

    deadline = "20/03/2025 12:00:00"
    time_left = get_time_left(deadline)
    
    # Xabar matni
    caption = (
        f"📢 <b>Open byudgetga ovoz bering va mukofot oling!</b>\n\n"
        f"Har bir ovoz uchun <b>50.000 so`m</b>dan to`lanmoqda\n"
        f"Ulgurib qoling vaqtimiz chegaralangan <b><i>{time_left}</i></b> vaqt qoldi\n"
        f"Har bir taklif qilingan do‘st uchun <b>5000 so‘m</b> mukofot olasiz! 🎉\n\n"
        f"https://t.me/{config.BOT_NAME}?start={message.from_user.id}\n\n"
        f"📩 Pastdagi tugma orqali botga to'g'ridan-to'g'ri ulanishingiz mumkin ⬇️"
    )

    await message.answer_photo(
        photo=photo_url,
        caption=caption,
        parse_mode="HTML",
        reply_markup=referral_button
    )
    


@router.message(lambda message: message.text == "📜 To‘lovlar tarixi")
async def payment_history_handler(message: types.Message):
    await message.answer("Siz hali hech qanday to‘lov amalga oshirmagansiz.")

@router.message(lambda message: message.text == "📞 Adminga murojaat")
async def contact_admin_handler(message: types.Message):
    await message.answer("Admin bilan bog‘lanish uchun: <b>@joinerdev</b>", parse_mode="HTML")



@router.message(lambda message: message.text == "📢 Xabar yuborish")
async def send_message_to_users(message: types.Message):
    if message.from_user.id != config.ADMIN_ID:
        return await message.answer("❌ Siz admin emassiz!")
    
    await message.answer("📩 Yuboriladigan xabarni kiriting:")

@router.message()
async def broadcast_message(message: types.Message):
    if message.from_user.id != config.ADMIN_ID:
        return
    
    text = message.text
    async with SessionLocal() as db:
        users = await db.execute(select(User.telegram_id))
        user_ids = users.scalars().all()

        for user_id in user_ids:
            try:
                await message.bot.send_message(user_id, text)
            except:
                pass  # Xatolarni e'tiborsiz qoldiramiz

    await message.answer("✅ Xabar barcha foydalanuvchilarga yuborildi!")
