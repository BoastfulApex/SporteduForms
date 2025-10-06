from aiogram.fsm.state import State, StatesGroup

class UserForm(StatesGroup):
    go_reg = State()
    