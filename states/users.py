from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    get_lang = State()          # Tilni tanlash
    get_filial = State()        # Filialni tanlash
    get_study_field = State()   # Ta'lim yo'nalishini tanlash
    get_group = State()         # Guruhni tanlash
    get_location = State()      # Joylashuvni tanlash
    check_user_status = State()
    question = State()
    text_answer = State()
    get_module = State()
