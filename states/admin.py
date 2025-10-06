from aiogram.fsm.state import State, StatesGroup

class EmployeeForm(StatesGroup):
    get_id = State()
    get_name = State()

class AddLocation(StatesGroup):
    waiting_for_location = State()

class SetEmployeeForm(StatesGroup):
    waiting_for_time_range = State()
    select_weekdays = State()
    confirm = State()

class ChartsForm(StatesGroup):
    get_date = State()