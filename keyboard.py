from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Oddiy ReplyKeyboard
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🗣 Ovoz berish"), KeyboardButton(text="👥 Do‘stlar taklif qilish")],
        [KeyboardButton(text="💰 Balans"), KeyboardButton(text="💳Kartalarim")],
        [KeyboardButton(text="📜 To‘lovlar tarixi"), KeyboardButton(text="📞 Adminga murojaat")]
    ],
    resize_keyboard=True  # Tugmalar o‘lchamini avtomatik moslash
)



def vote_buttons(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🗳 Ovoz berish 50.000 so'm", 
                url = f"https://t.me/ochiqbudjet_5_bot?start=050380051012"
            )]
        ]
    )



# Do‘stlar taklif qilish uchun tugma
def get_referral_button(bot_name, user_id):
    referral_link = f"https://t.me/{bot_name}?start={user_id}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🗳 Ovoz berish 50.000 so'm", url=referral_link)]
        ]
    )


balance_buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💳 Pulni yechish", callback_data = "withdraw_money"), 
         InlineKeyboardButton(text="➕ Karta qo‘shish", callback_data="add_card")]
    ]
)

# Agar karta raqami mavjud bo'lmasa, "Karta qo'shish" tugmasini ko'rsatish
def get_balance_buttons(has_card: bool):
    if has_card:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="💳 Pulni yechish", callback_data="withdraw_money")]
            ]
        )
    else:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="➕ Karta qo‘shish", callback_data="add_card")]
            ]
        )


# "Kartalarim" tugmasi bosilganda chiqadigan tugmalar
def get_cards_buttons():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Yana karta qo'shish", callback_data="add_card"), InlineKeyboardButton(text="🗑 O'chirish", callback_data="delete_card")]
        ]
    )


back_button = ReplyKeyboardMarkup(
    keyboard = [
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
    resize_keyboard=True
)
back_button_and_vote = ReplyKeyboardMarkup(
    keyboard = [
            [KeyboardButton(text="✅ Ovoz berdim")],
            [KeyboardButton(text="⬅️ Orqaga")]
        ],
    resize_keyboard=True
)



# Adminlar uchun menyu
admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📊 Umumiy statistika"), KeyboardButton(text="💰 To‘lovlarni tekshirish")],
        [KeyboardButton(text="📢 Xabar yuborish"), KeyboardButton(text="👤 Foydalanuvchilar ro‘yxati")],
        [KeyboardButton(text="⬅️ Orqaga")]
    ],
    resize_keyboard=True
)