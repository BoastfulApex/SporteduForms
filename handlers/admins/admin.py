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


