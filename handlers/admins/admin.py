from aiogram.types import ReplyKeyboardRemove, Message, WebAppData, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from loader import dp, bot
from keyboards.inline.menu_button import *
from keyboards.inline.main_inline import *
from utils.db_api.database import *
from aiogram.utils.deep_linking import decode_payload, encode_payload
from data import config
from aiogram.filters import Command, StateFilter, CommandObject, CommandStart
from aiogram import F, Router
from states.admin import EmployeeForm, AddLocation, SetEmployeeForm, ChartsForm
router = Router()
import json


dp.include_router(router)


channel_id = config.CHANNEL_ID

    
# @router.message(CommandStart, StateFilter(None))
# async def handler(message: Message, command: CommandStart):
#     check = await is_user_employee(message.from_user.id)
#     if check:
#         keyboard = await go_web_app()
#         await message.answer("Tugmani bosing", reply_markup=keyboard)
        
#     else:
#         encoded = encode_payload(message.from_user.id)
#         link = f"https://t.me/BoastfulApex_bot?start={encoded}"
#         await message.answer(f"⚠️ Siz xodim emassiz!\n\nBotdan foydalanish uchun xodim bo‘lishingiz kerak.\n\n")


@router.message(StateFilter(None), F.text  == '12')
async def handler(message: Message):
    markup = await admin_menu_keyboard()
    await message.answer("Kerakli buyruqni tanlang", reply_markup=markup)


@router.message(StateFilter(None), F.text  == '13')
async def handler(message: Message):
    encoded = encode_payload(message.from_user.id)
    link = f"https://t.me/BoastfulApex_bot?start={encoded}"
    await message.answer(link)

@router.message(StateFilter(None), F.text  == '11')
async def handler(message: Message):
    markup = await go_web_app()
    await message.answer("Kerakli buyruqni tanlang", reply_markup=markup)
    
    # markup = await admin_menu_keyboard()
    # await message.answer("Kerakli buyruqni tanlang", reply_markup=markup)


@router.message(F.text == "🔙 Bekor qilish")
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    markup = await admin_menu_keyboard()
    await message.answer("Kerakli buyruqni tanlang:", reply_markup=markup)


# Xodim qo‘shish boshlanishi
@router.message(F.text == "🧑‍💼 Xodim qo'shish")
async def start_add_employee(message: Message, state: FSMContext):
    markup = cancel  # bu cancel tugmasi bo'lgan keyboard
    await message.answer("Xodimning Telegram user_id sini kiriting:", reply_markup=markup)
    await state.set_state(EmployeeForm.get_id)


@router.message(F.text == "📊 Hisobotlar")
async def start_add_employee(message: Message, state: FSMContext):
    markup = cancel  # bu cancel tugmasi bo'lgan keyboard
    await message.answer("🕐 Endi ish boshlanish va tugash sanarini kiriting kiriting (24 soat formatda: HH:MM).\nMasalan: `01.01.2025 - 31.05.2025`", reply_markup=markup)
    await state.set_state(ChartsForm.get_date)


import re
from datetime import datetime
from aiogram import types

@router.message(ChartsForm.get_date)
async def process_date_range(message: Message, state: FSMContext):
    date_text = message.text.strip()

    # Regex to match: DD.MM.YYYY - DD.MM.YYYY
    pattern = r"^(\d{2})\.(\d{2})\.(\d{4})\s*-\s*(\d{2})\.(\d{2})\.(\d{4})$"
    match = re.match(pattern, date_text)

    if not match:
        await message.answer("❌ Noto‘g‘ri format! Iltimos, quyidagicha kiriting: `01.01.2025 - 31.05.2025`")
        return

    # Convert to datetime to validate real dates
    try:
        start_date = datetime.strptime(f"{match.group(1)}.{match.group(2)}.{match.group(3)}", "%d.%m.%Y")
        end_date = datetime.strptime(f"{match.group(4)}.{match.group(5)}.{match.group(6)}", "%d.%m.%Y")
    except ValueError:
        await message.answer("❌ Sana mavjud emas. Iltimos, haqiqiy sanalarni kiriting.")
        return

    if start_date > end_date:
        await message.answer("❌ Boshlanish sanasi tugash sanasidan oldin bo‘lishi kerak.")
        return

    # ✅ To‘g‘ri bo‘lsa, holatni yangilang yoki keyingi bosqichga o‘ting
    
    file_path = await generate_attendance_excel_file(start_date=start_date, end_date=end_date, user_id=message.from_user.id)
    file = FSInputFile(file_path, filename="hisobot.xlsx")
    await message.answer_document(file, caption="📊 Hisobot tayyor!")
    await message.answer(f"✅ Sana oralig‘i qabul qilindi:\n📅 {start_date.date()} — {end_date.date()}")


# ID qabul qilish
@router.message(F.text, EmployeeForm.get_id)
async def process_user_id(message: Message, state: FSMContext):
    await state.update_data(user_id=message.text)
    markup = cancel
    await message.answer("Xodimning to‘liq ismini kiriting:", reply_markup=markup)
    await state.set_state(EmployeeForm.get_name)


# To‘liq ism qabul qilish va saqlash
@router.message(F.text, EmployeeForm.get_name)
async def process_full_name(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data['user_id']
    full_name = message.text
    print(message.from_user.id)
    print("AAAAAA")
    await add_employee(admin_id= message.from_user.id, user_id=user_id, full_name=full_name)
    await state.clear()
    markup = await admin_menu_keyboard()
    await message.answer("✅ Xodim qo‘shildi!\n\nKerakli buyruqni tanlang:", reply_markup=markup)
    

@router.message(StateFilter(None), F.text == "📍 Manzillar")
async def show_latest_location(message: Message):
    location = await get_filial_location(message.from_user.id)
    
    if location:
        markup = address_bottom_keyboard()
        name = location.name or "Noma'lum manzil"
        await message.answer(f"📍 So‘nggi manzil: {name}", reply_markup=markup)

        if location.latitude and location.longitude:
            await message.answer_location(latitude=location.latitude, longitude=location.longitude)
        else:
            await message.answer("⚠️ Ushbu manzil uchun koordinatalar mavjud emas.")
    else:
        markup = empty_address_keyboard()
        await message.answer("❌ Hozircha manzillar mavjud emas.", reply_markup=markup)
        

@router.message(StateFilter(None), F.text == "➕ Manzil qo‘shish")
async def ask_for_location(message: Message, state: FSMContext):
    await message.answer("📍 Iltimos, yangi manzil lokatsiyasini yuboring (Telegram joylashuv orqali).")
    await state.set_state(AddLocation.waiting_for_location)


@router.message(StateFilter(None), F.text == "✏️ Manzilni yangilash")
async def ask_for_location(message: Message, state: FSMContext):
    await message.answer("📍 Iltimos, yangi manzil lokatsiyasini yuboring (Telegram joylashuv orqali).")
    await state.set_state(AddLocation.waiting_for_location)


@router.message(AddLocation.waiting_for_location, F.location)
async def save_user_location(message: Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude

    name = await get_location_name(lat, lon)

    await save_location(name=name, lat=lat, lon=lon, user_id=message.from_user.id)

    await message.answer(f"✅ Manzil qo‘shildi:\n📍 {name}")
    markup = await admin_menu_keyboard()
    await message.answer("Kerakli bo‘limni tanlang:", reply_markup=markup)

    await state.clear()
    

@router.callback_query(lambda c: c.data.startswith("approve_user:"))
async def approve_user_callback(callback_query: CallbackQuery, state: FSMContext):
    user_id = int(callback_query.data.split(":")[1])
    
    user = await callback_query.bot.get_chat(user_id)

    await add_employee(user_id=user_id, full_name=f"{user.first_name} {user.last_name or ''}".strip(), admin_id=callback_query.from_user.id)

    # 3. Adminga xabarni yangilash
    await callback_query.message.edit_text("🟢 Foydalanuvchi tasdiqlandi va bazaga qo‘shildi.")        
    await state.update_data(selected_weekdays=set(), employee_id=user_id)
    

    selected_set = set()
    keyboard = generate_weekday_keyboard(selected_set)

    await callback_query.bot.send_message(chat_id=callback_query.from_user.id, text="📆 Iltimos, ishlanadigan hafta kunlarini tanlang:", reply_markup=keyboard)

    

@router.callback_query(lambda c: c.data.startswith("reject_user:"))
async def reject_user_callback(callback_query: CallbackQuery):
    user_id = int(callback_query.data.split(":")[1])

    await callback_query.bot.send_message(
        chat_id=user_id,
        text="❌ Administrator sizning so‘rovingizni rad etdi."
    )
    await delete_employee_by_user_id(user_id)
    await callback_query.message.edit_text("🔴 Foydalanuvchi rad etildi.")
    await callback_query.answer("Rad javobi yuborildi.")


@router.callback_query(lambda c: c.data.startswith("select_weekday:"))
async def select_weekday_callback(callback: CallbackQuery, state: FSMContext):
    weekday_name = callback.data.split(":")[1]
    data = await state.get_data()
    selected = data.get("selected_weekdays", set())

    # toggle tanlash
    if weekday_name in selected:
        selected.remove(weekday_name)
    else:
        selected.add(weekday_name)

    await state.update_data(selected_weekdays=selected)
    keyboard = generate_weekday_keyboard(selected)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()
    
    
@router.callback_query(lambda c: c.data == "continue_schedule")
async def continue_to_time(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    selected = data.get("selected_weekdays", set())

    if not selected:
        await callback.answer("⛔ Hech qanday kun tanlanmagan.", show_alert=True)
        return

    await callback.message.edit_text("🕐 Endi ish boshlanish va tugash vaqtlarini kiriting (24 soat formatda: HH:MM).\nMasalan: `09:00 - 18:00`")
    await state.set_state(SetEmployeeForm.waiting_for_time_range)


@router.message(SetEmployeeForm.waiting_for_time_range, F.text)
async def receive_time_range(message: Message, state: FSMContext):
    text = message.text.strip()
    try:
        start_str, end_str = map(str.strip, text.split("-"))
        from datetime import datetime
        start_time = datetime.strptime(start_str, "%H:%M").time()
        end_time = datetime.strptime(end_str, "%H:%M").time()

        if start_time >= end_time:
            raise ValueError("Boshlanish vaqti tugash vaqtidan keyin bo‘lmasligi kerak.")

        await state.update_data(start=start_time, end=end_time)

        # Endi saqlash
        data = await state.get_data()
        user_id = message.from_user.id

        await save_work_schedule(user_id, data)
        await message.answer("✅ Ish jadvali muvaffaqiyatli saqlandi!")
        jadval_text = await get_employee_schedule_text(data['employee_id'])

        await bot.send_message(
            chat_id=data['employee_id'],
            text=f"✅ Administrator sizni tasdiqladi. Siz endi ishchi sifatida ro‘yxatdan o‘tdingiz!\n\n{jadval_text}"
        )

        await state.clear()

        await state.clear()

    except Exception as e:
        await message.answer(f"⛔ Noto‘g‘ri format: {e}. Iltimos, `09:00 - 18:00` ko‘rinishida yozing.")
        

@router.callback_query(lambda c: c.data == "back_to_start")
async def back_to_start(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("employee_id")
    [print(f"User ID: {user_id}")]
    
    user = await get_telegram_user(user_id)

    keyboard = get_user_approval_keyboard(user_id)

    await callback.message.edit_text(
        text=f"🚨 Yangi foydalanuvchi botga kirishga harakat qildi:\n\n"
             f"👤 Ismi: {user.first_name} {user.last_name}\n"
             f"🆔 Telegram ID: {user.user_id}\n\n"
             f"Ushbu foydalanuvchini tasdiqlaysizmi?",
        reply_markup=keyboard
    )
    await callback.answer()


@router.channel_post(F.text.in_(['SendPostNotification']))
async def send_report(message: types.Message):
    for filial in Filial.objects.all():
        report = await get_daily_report(filial)
        admins = Administrator.objects.filter(filial=filial).all()
        for admin in admins:
            if admin.telegram_id:
                try:
                    await bot.send_message(
                        chat_id=admin.telegram_id,
                        text=f"📊 {filial.filial_name} uchun kunlik hisobot:\n\n{report}"
                    )
                except:
                    pass