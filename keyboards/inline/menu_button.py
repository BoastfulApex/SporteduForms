from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from apps.main.models import Filial, Location, StudyField, Group


def lang_keyboard():
    """Til tanlash"""
    key1 = KeyboardButton(text=f"🇺🇿 O'zbek tili")
    key2 = KeyboardButton(text=f"🇷🇺 Русский язык")
    keyboard = ReplyKeyboardMarkup(keyboard=[[key1, key2]], resize_keyboard=True)
    return keyboard


def filial_keyboard(lang):
    """Filial tanlash"""
    filials = Filial.objects.all()
    keyboards = []
    for f in filials:
        text = f.name_uz if lang == "uz" else f.name_ru
        keyboards.append([KeyboardButton(text=text)])
    keyboard = ReplyKeyboardMarkup(keyboard=keyboards, resize_keyboard=True)
    return keyboard


def study_field_keyboard(lang):
    """Ta'lim yo‘nalishini tanlash"""
    fields = StudyField.objects.all()
    keyboards = []
    for i in fields:
        text = i.study_field_uz if lang == "uz" else i.study_field_ru
        keyboards.append([KeyboardButton(text=text)])
    keyboard = ReplyKeyboardMarkup(keyboard=keyboards, resize_keyboard=True)
    return keyboard


def group_keyboard(lang, study_field=None, filial=None):
    """Guruhni tanlash — faqat tanlangan filial va yo‘nalish bo‘yicha"""
    groups = Group.objects.all()
    if study_field:
        groups = groups.filter(study_field=study_field)
    if filial:
        groups = groups.filter(filial=filial)
    
    keyboards = []
    for g in groups:
        text = g.name_uz if lang == "uz" else g.name_ru
        keyboards.append([KeyboardButton(text=text)])
    keyboard = ReplyKeyboardMarkup(keyboard=keyboards, resize_keyboard=True)
    return keyboard


async def location_keyboard(lang):
    """Manzil (location) tanlash"""
    stm_all = Location.objects.all()
    keyboards = []
    for i in stm_all:
        text = i.location_uz if lang == "uz" else i.location_ru
        keyboards.append([KeyboardButton(text=text)])
    keyboard = ReplyKeyboardMarkup(keyboard=keyboards, resize_keyboard=True)
    return keyboard


async def phone_keyboard(lang):
    """Telefon raqam ulashish"""
    texts = {
        "uz": ["Raqamni ulashish", "Ortga"],
        "ru": ["Поделиться номером", "Назад"],
    }[lang]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    key1 = KeyboardButton(text=f"📞 {texts[0]}", request_contact=True)
    key2 = KeyboardButton(text=f"⬅️️ {texts[1]}")
    keyboard.add(key1)
    keyboard.add(key2)
    return keyboard


async def user_menu(lang):
    """Foydalanuvchi asosiy menyusi"""
    texts = {
        "uz": ["Oila kursi haqida", "Fikr qoldirish"],
        "ru": ["О курсе", "Оставить отзыв"],
    }[lang]
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    key1 = KeyboardButton(text=f"📚 {texts[0]}")
    key2 = KeyboardButton(text=f"✍️ {texts[1]}")
    keyboard.add(key1, key2)
    return keyboard


def back_keyboard(lang):
    """Orqaga tugmasi"""
    text = "⬅️️ Orqaga" if lang == "uz" else "⬅️️ Назад"
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text=text))
    return keyboard


def rating_keyboard():
    """Ovoz berish"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text="📊 Ovoz berish"))
    return keyboard


async def group_keyboard(lang, groups):
    """Joriy oydagi guruhlar uchun keyboard"""
    keyboards = []
    print(groups)
    for g in groups:
        text = g.name_uz if lang == "uz" else g.name_ru
        keyboards.append([KeyboardButton(text=text)])

    return ReplyKeyboardMarkup(keyboard=keyboards, resize_keyboard=True)