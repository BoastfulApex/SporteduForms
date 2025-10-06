from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from apps.main.models import *
from utils.db_api.database import *
from data.config import URL


async def go_web_app():
    print(URL)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Kirish",
                web_app=WebAppInfo(url=URL))]
        ]
    )
    return keyboard


def generate_weekday_keyboard(selected_ids: set[int]) -> InlineKeyboardMarkup:
    keyboard = []

    for weekday in ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]:
        # Weekday obyektini olish
        button_text = f"✅ {weekday}" if weekday in selected_ids else weekday
        callback_data = f"select_weekday:{weekday}"
        keyboard.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])

    # Pastki tugmalar: Davom etish va Orqaga
    keyboard.append([
        InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_start"),
        InlineKeyboardButton(text="⏭ Davom etish", callback_data="continue_schedule")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_user_approval_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_user:{user_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_user:{user_id}")
        ]
    ])
    
async def get_filial_selection_keyboard() -> InlineKeyboardMarkup:
    filiallar = await get_all_filials()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=filial.filial_name, callback_data=f"filial_{filial.id}")]
            for filial in filiallar
        ]
    )
    return keyboard