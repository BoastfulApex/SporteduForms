from aiogram.types import ReplyKeyboardRemove, Message, CallbackQuery
from loader import dp, bot
from keyboards.inline.menu_button import *
from keyboards.inline.main_inline import *
from utils.db_api.database import *
from data import config
from aiogram.filters import Command, StateFilter, CommandObject, CommandStart
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from states.users import Form
from aiogram import types


router = Router()


dp.include_router(router)


channel_id = config.CHANNEL_ID

CHANNEL_ID = -1001312046890  # Kanal ID'si
CHANNEL_LINK = "https://t.me/minsport_institut"  # Kanal havolasi


async def check_membership(user_id):
    try:
        chat_member = await bot.get_chat_member(CHANNEL_ID, user_id)
        if chat_member.status in ["member", "administrator", "creator"]:
            return True
        else:
            return False  # Agar left, kicked yoki restricted bo‘lsa
    except Exception as e:
        print(f"Error checking membership: {e}")
        return False  # Agar xatolik bo‘lsa, a'zo emas deb qabul qilamiz


# /start
@router.message(CommandStart(), StateFilter(None))
async def bot_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    is_member = await check_membership(user_id)

    if not is_member:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="✅ A'zolikni tekshirish")]],
            resize_keyboard=True
        )
        await message.answer(
            f"📢 Hurmatli foydalanuvchi, botdan foydalanish uchun quyidagi kanalga a'zo bo‘ling:\n"
            f"{CHANNEL_LINK}\n\n"
            f"A'zolikni tekshirish uchun pastdagi tugmani bosing.",
            reply_markup=keyboard
        )
        await state.set_state(Form.check_user_status)
        return

    user_check = await check_user(user_id)
    if user_check:
        lang = await get_lang(user_id)
        text = 'Javoblaringiz uchun rahmat.' if lang != 'ru' else 'Спасибо за ваши ответы.'
        await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
        await state.set_state(Form.get_age)
    else:
        text = ("👉 Assalomu alaykum, hurmatli tinglovchi!\n"
                "Siz Jismoniy tarbiya va sport bo‘yicha mutaxassislarni qayta tayyorlash va malakasini oshirish institutining so‘rovnomasida ishtirok etmoqdasiz."
                "\nIltimos, savollarga diqqat bilan va samimiy javob bering.\n\nIltimos kerakli tilni tanlang 👇"
                "\n\nЗдравствуйте. Пожалуйста выберите нужный язык 👇")
        await message.answer(text=text, reply_markup=lang_keyboard())
        await state.set_state(Form.get_lang)


# A’zolikni qayta tekshirish
@router.message(StateFilter(Form.check_user_status))
async def check_user_membership(message: Message, state: FSMContext):
    user_id = message.from_user.id
    is_member = await check_membership(user_id)

    if not is_member:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="✅ A'zolikni tekshirish")]],
            resize_keyboard=True
        )
        await message.answer(
            f"📢 Hurmatli foydalanuvchi, botdan foydalanish uchun quyidagi kanalga a'zo bo‘ling:\n"
            f"{CHANNEL_LINK}\n\n"
            f"A'zolikni tekshirish uchun pastdagi tugmani bosing.",
            reply_markup=keyboard
        )
        return

    user_check = await check_user(user_id)
    if user_check:
        lang = await get_lang(user_id)
        text = 'Javoblaringiz uchun rahmat.' if lang != 'ru' else 'Спасибо за ваши ответы.'
        await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
        await state.set_state(Form.get_age)
    else:
        text = ("👉 Assalomu alaykum, hurmatli tinglovchi!\n"
                "Iltimos kerakli tilni tanlang 👇\n\nЗдравствуйте. Пожалуйста выберите нужный язык 👇")
        await message.answer(text=text, reply_markup=lang_keyboard())
        await state.set_state(Form.get_lang)


# Til tanlash
@router.message(StateFilter(Form.get_lang))
async def get_lang_func(message: Message, state: FSMContext):
    lang = 'ru' if message.text == '🇷🇺 Русский язык' else 'uz'
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username

    await add_user(user_id=user_id, first_name=first_name, username=username, lang=lang)

    text = "Qaysi hududda faoliyat yuritasiz?" if lang == "uz" else "В какой области вы работаете?"
    await message.answer(text=text, reply_markup=await location_keyboard(lang))
    await state.set_state(Form.get_location)


# Hudud tanlash
@router.message(StateFilter(Form.get_location))
async def get_location_func(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    await set_location(loc_name=message.text, user_id=message.from_user.id)
    text = "Iltimos, siz o'qiyotgan ta'lim muassasasini tanlang 👇" if lang == 'uz' else 'Пожалуйста, выберите учебное заведение, которое вы посещаете 👇'
    await message.answer(text=text, reply_markup=filial_keyboard(lang))
    await state.set_state(Form.get_filial)


# Filial tanlash
@router.message(StateFilter(Form.get_filial))
async def get_filial_func(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    await set_filial(user_id=message.from_user.id, filial_name=message.text)
    text = "Qaysi yo'nalishda ta'lim olyapsiz?" if lang == 'uz' else "На каком направлении вы обучаетесь?"
    await message.answer(text=text, reply_markup=study_field_keyboard(lang))
    await state.set_state(Form.get_study_field)


@router.message(StateFilter(Form.get_study_field))
async def get_study_field_func(message: Message, state: FSMContext):
    lang = await get_lang(message.from_user.id)
    study_field_name = message.text

    # Tanlangan yo‘nalishni saqlash
    study_field = await set_study_field(user_id=message.from_user.id, name=study_field_name)

    filial = await get_filial_from_db(message.from_user.id)

    now = datetime.now()
    current_month = now.month
    current_year = now.year

    # Guruhlarni topish (modelingizdagi sana maydoni bo‘yicha to‘g‘rilang)
    groups = Group.objects.filter(
        filial=filial,
        study_field=study_field,
        month__month=current_month,
        year__year=current_year
    )
    if not groups.exists():
        text = (
            "Bu yo‘nalishda joriy oydagi guruhlar topilmadi."
            if lang == "uz"
            else "Нет групп для этого направления в текущем месяце."
        )
        await message.answer(text=text)
        return
    else:
        text = "Guruhingizni tanlang:" if lang == "uz" else "Выберите свою группу:"
        await message.answer(
            text=text,
            reply_markup=ReplyKeyboardRemove()
        )

    # Inline keyboard yaratish
    keyboard = await inline_group_keyboard(lang=lang, groups=groups)

    text = "Guruhlar" if lang == "uz" else "Группы"
    await message.answer(text=text, reply_markup=keyboard)
    await state.set_state(Form.get_group)


@router.callback_query(Form.get_group)
async def get_group_func(callback: CallbackQuery, state: FSMContext):
    lang = await get_lang(callback.from_user.id)
    data = callback.data

    # Orqaga tugmasi bosilsa
    if data == "back_to_study_field":
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(
            text = "Qaysi yo'nalishda ta'lim olyapsiz?" if lang == 'uz' else "На каком направлении вы обучаетесь?",
            reply_markup=study_field_keyboard(lang)
        )
        await state.set_state(Form.get_study_field)
        return

    # Guruh tanlanganda
    if data.startswith("group_"):
        group_id = int(data.split("_")[1])
        user_id = callback.from_user.id
        await state.update_data(group_id=group_id)
        # Talaba yaratish
        student = await create_student(user_id=user_id, group_id=group_id)

        # Eski inline keyboardni o‘chirish
        await callback.message.edit_reply_markup(reply_markup=None)

        if not student:
            text = "❌ Talaba yaratishda xatolik yuz berdi." if lang == "uz" else "❌ Ошибка при создании студента."
            await callback.message.answer(text=text)
            await state.clear()
            await state.set_state(Form.get_study_field)


        # Faol modullarni olish
        active_modules = await get_active_modules(group_id)

        if not active_modules:
            text = "Bu guruh uchun faol modullar topilmadi." if lang == "uz" else "Нет активных модулей для этой группы."
            await callback.message.answer(text=text)
            await callback.message.answer(
                text = "Qaysi yo'nalishda ta'lim olyapsiz?" if lang == 'uz' else "На каком направлении вы обучаетесь?",
                reply_markup=study_field_keyboard(lang)
            )            
            return

        # Modul tanlash uchun inline keyboard
        keyboard = await inline_module_keyboard(lang, active_modules)
        text = "Faningizni tanlang:" if lang == "uz" else "Выберите свой модуль:"
        await callback.message.answer(text=text, reply_markup=keyboard)
        await state.set_state(Form.get_module)
        

@router.callback_query(StateFilter(Form.get_module))
async def get_module_func(call: CallbackQuery, state: FSMContext):
    lang = await get_lang(call.from_user.id)
    data = call.data

    if data.startswith("module_"):
        module_id = int(data.split("_")[1])
        await state.update_data(module_id=module_id)

        data_state = await state.get_data()
        group_id = data_state.get("group_id")

        # 🔹 Shu modul uchun form_category ni topamiz
        form_category = await get_form_category()
        if not form_category:
            await call.message.answer(
                "❌ Ushbu modul uchun so‘rovnoma topilmadi."
                if lang == "uz"
                else "❌ Для этого модуля нет анкеты."
            )
            await state.clear()
            return

        # 🔹 Savollarni olish
        questions = await get_questions(form_category.id)
        if not questions:
            await call.message.answer(
                "❌ Faol savollar topilmadi."
                if lang == "uz"
                else "❌ Активные вопросы не найдены."
            )
            await state.clear()
            return

        start_text = "So‘rovnoma boshlandi!" if lang == "uz" else "Опрос начался!"
        await call.message.answer(start_text)

        # Birinchi savolni olish
        first_question = questions[0]
        text = first_question.question_uz if lang == "uz" else first_question.question_ru

        # Agar text_answer bo‘lsa, yozma javob kerakligi haqida xabar
        if first_question.text_answer:
            extra_text = (
                "\n\n✍️ Iltimos, savolga yozma ravishda javob bering."
                if lang == "uz"
                else "\n\n✍️ Пожалуйста, ответьте на вопрос письменно."
            )
            text += extra_text

            # Oldingi xabarni o‘chirib, yangi savolni yuborish
            await call.message.delete()
            await call.message.answer(text=text, parse_mode="HTML")
            await state.set_state(Form.text_answer)
            await state.update_data(question_id=first_question.id)                   

        else:
            # Agar bu variantli savol bo‘lsa, keyboard yuboramiz
            keyboard = answers_keyboard(
                question_id=first_question.id,
                lang=lang,
                user_id=call.from_user.id
            )
            await call.message.delete()
            await call.message.answer(text=text, reply_markup=keyboard, parse_mode="HTML")
            await state.set_state(Form.question)
            await state.update_data(question_id=first_question.id)                   
                
                
@router.callback_query(StateFilter(Form.question))
async def questions(call: types.CallbackQuery, state: FSMContext):
    print('AAAA')
    lang = await get_lang(call.from_user.id)
    data = await state.get_data()

    index = int(data.get('index', 0))
    group_id = data.get('group_id')
    module_id = data.get('module_id')  # <-- modulni state dan olamiz

    answer_id = call.data
    form_category = FormCategory.objects.filter(active=True).first()
    questions = list(
        Question.objects.filter(form_category=form_category, active=True).order_by("id")
    )

    old_question = questions[index]
    user = TelegramUser.objects.filter(telegram_id=call.from_user.id).first()
    student = Student.objects.filter(telegram_user=user, group_id=group_id).first()
    answer = Answer.objects.get(id=int(answer_id))

    # 🟢 get_or_create ishlatyapmiz
    ua, created = UserAnswer.objects.get_or_create(
        user=student,
        question=old_question,
        module_id=module_id,  # module_id ni ham qo‘shamiz
    )

    # Agar answer hali bog‘lanmagan bo‘lsa, qo‘shamiz
    ua.answer.add(answer)
    ua.save()

    index += 1
    await state.update_data(index=index)

    if index >= len(questions):
        group_id = data.get("group_id")  # group_id ni state dan olamiz

        await call.message.delete()

        finish_text = (
            "✅ Siz ushbu modul bo‘yicha savollarga javob berishni tugatdingiz.\n\n"
            "⬅️ Quyidagi tugma orqali modullar ro‘yxatiga qayting."
            if lang == "uz"
            else "✅ Вы завершили ответы на вопросы по этому модулю.\n\n"
                 "⬅️ Перейдите к списку модулей по кнопке ниже."
        )

        # 🔹 Modullar ro‘yxatiga qaytish uchun keyboard
        keyboard = modules_keyboard(group_id=group_id, lang=lang)

        await bot.send_message(
            chat_id=call.from_user.id,
            text=finish_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

        await state.set_state(Form.get_module)
        return

    question = questions[index]
    text = question.question_uz if lang == "uz" else question.question_ru
    if question.text_answer:
        extra_text = (
            "\n\n✍️ Iltimos, savolga yozma ravishda javob bering."
            if lang == "uz"
            else "\n\n✍️ Пожалуйста, ответьте на вопрос письменно."
        )
        text += extra_text

        # Oldingi xabarni o‘chirib, yangi savolni yuborish
        await call.message.delete()
        await call.message.answer(text=text, parse_mode="HTML")
        await state.set_state(Form.text_answer)
        await state.update_data(question_id=question.id)                   

    else:
        # Agar bu variantli savol bo‘lsa, keyboard yuboramiz
        keyboard = answers_keyboard(
            question_id=question.id,
            lang=lang,
            user_id=call.from_user.id
        )
        await call.message.delete()
        await call.message.answer(text=text, reply_markup=keyboard, parse_mode="HTML")
        await state.set_state(Form.question)
        await state.update_data(question_id=question.id)                   


@router.message(StateFilter(Form.text_answer))
async def text_answer_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    print(message.text)
    lang = await get_lang(message.from_user.id)

    question_id = data.get("question_id")
    group_id = data.get("group_id")
    module_id = data.get("module_id")
    index = int(data.get("index", 0))

    text_answer = message.text.strip()

    # 🔹 Studentni topamiz
    telegram_user = TelegramUser.objects.filter(telegram_id=message.from_user.id).first()
    user = Student.objects.filter(telegram_user=telegram_user, group_id=group_id).first()

    # 🔹 get_or_create bilan UserAnswer ni yangilaymiz
    ua, created = UserAnswer.objects.get_or_create(
        user=user,
        question_id=question_id,
        module_id=module_id
    )
    ua.text_answer = text_answer
    ua.save()

    # 🔹 Keyingi savolga o‘tamiz
    form_category = FormCategory.objects.filter(active=True).first()
    questions = list(Question.objects.filter(form_category=form_category, active=True).order_by("id"))
    index += 1
    await state.update_data(index=index)

    if index >= len(questions):
        # 🔚 Barcha savollar yakunlandi
        finish_text = (
            "✅ Siz ushbu modul bo‘yicha savollarga javob berishni tugatdingiz.\n\n"
            "⬅️ Quyidagi tugma orqali modullar ro‘yxatiga qayting."
            if lang == "uz"
            else "✅ Вы завершили ответы на вопросы по этому модулю.\n\n"
                 "⬅️ Перейдите к списку модулей по кнопке ниже."
        )

        keyboard = modules_keyboard(group_id=group_id, lang=lang)

        await message.answer(finish_text, reply_markup=keyboard, parse_mode="HTML")
        await state.clear()
        return

    # 🔹 Keyingi savolni yuboramiz
    next_question = questions[index]
    text = next_question.question_uz if lang == "uz" else next_question.question_ru

    if next_question.text_answer:
        # Agar yozma javobli bo‘lsa
        extra_text = (
            "\n\n✍️ Iltimos, savolga yozma ravishda javob bering."
            if lang == "uz"
            else "\n\n✍️ Пожалуйста, ответьте на вопрос письменно."
        )
        text += extra_text

        await message.answer(text, parse_mode="HTML")
        await state.set_state(Form.text_answer)
        await state.update_data(question_id=next_question.id)
    else:
        # Agar variantli savol bo‘lsa
        keyboard = answers_keyboard(
            question_id=next_question.id,
            lang=lang,
            user_id=message.from_user.id
        )
        await message.answer(text=text, reply_markup=keyboard, parse_mode="HTML")
        await state.set_state(Form.question)
