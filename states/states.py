from aiogram.fsm.state import StatesGroup, State

class AddItem(StatesGroup):
    title = State()
    description = State()
    location = State()
    photo = State()

class ShowItem(StatesGroup):
    item_id = State()

class ShowClaims(StatesGroup):
    item_id = State()
