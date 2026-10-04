from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def main():
    main = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='➕ Добавить'), KeyboardButton(text='📚 Вещи')],
            [KeyboardButton(text='📊 Мои заявки')]
        ],
        resize_keyboard=True
    )
    return main

def cancel():
    cancel = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='❌ Отмена')]
        ],
        resize_keyboard=True
    )
    return cancel

def items_board(items):
    buttons = []
    for i in items:
        buttons.append([InlineKeyboardButton(text='Подробнее', callback_data=f"item:show:{i['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def item_board(item_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🙋 Это моё', callback_data=f'claim:create:{item_id}')]
    ])

def claims_board(claims):
    buttons = []
    for i in claims:
        buttons.append([InlineKeyboardButton(text='✅ Передано', callback_data=f"claim:approve:{i['id']}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
