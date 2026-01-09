from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from apps.main.models import *
from utils.db_api.database import *
from data.config import URL
from aiogram.utils.keyboard import InlineKeyboardBuilder


# def answers_keyboard(question_id, lang, user_id=None):
#     builder = InlineKeyboardBuilder()
#     answers = Answer.objects.filter(question_id=question_id).all()
#     question = Question.objects.get(id=question_id)

#     if not question.multi_answer:
#         # Multi-answer emas
#         for answer in answers:
#             if lang == 'uz':
#                 builder.row(
#                     InlineKeyboardButton(text=answer.answer_uz, callback_data=str(answer.id))
#                 )
#             else:
#                 builder.row(
#                     InlineKeyboardButton(text=answer.answer_ru, callback_data=str(answer.id))
#                 )
#     else:
#         # Multi-answer bo‘lsa
#         user = TelegramUser.objects.filter(telegram_id=user_id).first()
#         user_answer, created = UserAnswer.objects.get_or_create(
#             user=user,
#             question=question
#         )
#         user_answer.save()

#         go_text = "Перейти к следующему вопросу ➡️"
#         for answer in answers:
#             text = answer.answer_ru
#             if lang == 'uz':
#                 text = answer.answer_uz
#                 back_text = "⬅️️ Orqaga"
#                 go_text = "Keyingi savolga o'tish ➡️"

#             if answer in user_answer.answer.all():
#                 text = f'✅ {text}'
#             builder.row(
#                 InlineKeyboardButton(text=text, callback_data=str(answer.id))
#             )

#         builder.row(
#             InlineKeyboardButton(text=go_text, callback_data='go_next')
#         )

#     back_text = "⬅️️ Назад"
#     if lang == 'uz':
#         back_text = "⬅️️ Orqaga"

#     builder.row(
#         InlineKeyboardButton(text=back_text, callback_data='go_back')
#     )

#     # Tayyor markupni qaytarish
#     return builder.as_markup()


def answers_keyboard(question_id, lang, user_id=None):
    builder = InlineKeyboardBuilder()
    answers = Answer.objects.filter(question_id=question_id)
    question = Question.objects.get(id=question_id)

    # Text-answer bo‘lsa, variantlar chiqmaydi
    if question.text_answer:
        return None

    for answer in answers:
        text = answer.answer_uz if lang == "uz" else answer.answer_ru
        builder.row(InlineKeyboardButton(text=text, callback_data=str(answer.id)))

    return builder.as_markup()


async def inline_group_keyboard(lang, groups):
    """Guruhlarni inline keyboard sifatida chiqarish"""
    buttons = []

    for g in groups:
        text = g.name_uz if lang == "uz" else g.name_ru
        # callback_data orqali guruh ID yuboriladi
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"group_{g.id}")])

    # Orqaga tugmasi
    back_text = "◀️ Orqaga" if lang == "uz" else "◀️ Назад"
    buttons.append([InlineKeyboardButton(text=back_text, callback_data="back_to_study_field")])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def inline_module_keyboard(lang, modules):
    buttons = [
        [InlineKeyboardButton(
            text=m.study_module.name,
            callback_data=f"module_{m.id}"
        )]
        for m in modules
    ]
    back_text = "◀️ Orqaga" if lang == "uz" else "◀️ Назад"
    buttons.append([InlineKeyboardButton(text=back_text, callback_data="back_to_group")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def modules_keyboard(group_id: int, lang: str) -> InlineKeyboardMarkup:
    modules = GroupModuleTeacher.objects.filter(group_id=group_id, active=True)

    keyboard = InlineKeyboardMarkup(row_width=1)

    if not modules.exists():
        text = "📭 Hozircha hech qanday modul mavjud emas." if lang == "uz" else "📭 Пока нет доступных модулей."
        keyboard.add(InlineKeyboardButton(text=text, callback_data="no_modules"))
        return keyboard

    # 🔹 Har bir modul uchun tugma
    for m in modules:
        module_name = (
            m.study_module.name_uz if lang == "uz" else m.study_module.name_ru
        )
        callback_data = f"module_{m.id}"
        keyboard.add(InlineKeyboardButton(text=f"📘 {module_name}", callback_data=callback_data))

    # 🔹 Orqaga qaytish tugmasi
    back_text = "⬅️ Guruhlar ro‘yxatiga qaytish" if lang == "uz" else "⬅️ Вернуться к списку групп"
    keyboard.add(InlineKeyboardButton(text=back_text, callback_data="back_to_groups"))

    return keyboard