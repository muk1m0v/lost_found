from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from board import *
from service import *

router = Router()

def get_id(data, prefix):
    raw = data[len(prefix):]
    if not raw.isdigit():
        return None
    value = int(raw)
    if value <= 0:
        return None
    return value

def item_text(item):
    return f"🔹 {item['title']}\n\nОписание: {item['description']}\n📍 Место: {item['location']}"

@router.message(CommandStart())
async def start(message: Message):
    user = message.from_user
    is_login = await check_users(user.id)
    if not is_login:
        await save_user(user.id, user.username, user.full_name)
    text = f'Welcome, <b>{user.full_name}</b>'
    await message.answer(text, parse_mode='HTML', reply_markup=main())

@router.message(Command('items'))
@router.message(F.text == '📚 Вещи')
@router.message(F.text == '📚 Список найденных вещей')
async def tasks(message: Message):
    rows = await get_items()
    if not rows:
        await message.answer('Список пуст.')
        return
    text = 'Выберите вещь:\n\n'
    for i in rows:
        text += f"🔹 {i['title']}\n"
    await message.answer(text, reply_markup=items_board(rows))

@router.message(Command('my_claims'))
@router.message(F.text == '📊 Мои заявки')
async def my_list(message: Message):
    user = message.from_user
    rows = await my_claims(user.id)
    if not rows:
        await message.answer('У вас пока нет заявок.')
        return
    text = 'Ваши заявки:\n\n'
    for i in rows:
        text += f"Вещь: {i['title']} — статус заявки: {i['status']}\n"
    await message.answer(text)

@router.message(Command('help'))
async def help(message: Message):
    await message.answer('/start - запуск бота\n/help - помощь\n/items - список доступных вещей\n/item - карточка вещи\n/my_claims - мои заявки\n/claims - заявки на твою вещь\n/add_item - добавить вещь\n/cancel - отменить ввод')

@router.callback_query(F.data.startswith('item:show:'))
async def show_item(callback: CallbackQuery):
    await callback.answer()
    item_id = get_id(callback.data, 'item:show:')
    if item_id is None:
        await callback.message.answer('Некорректная кнопка.')
        return
    item = await get_item(item_id)
    if item is None:
        await callback.message.answer('Вещь не найдена (устаревшая кнопка).')
        return
    await callback.message.answer_photo(photo=item['photo_file_id'], caption=item_text(item), reply_markup=item_board(item['id']))

@router.callback_query(F.data.startswith('claim:create:'))
async def make_claim(callback: CallbackQuery):
    await callback.answer()
    user = callback.from_user
    item_id = get_id(callback.data, 'claim:create:')
    if item_id is None:
        await callback.message.answer('Некорректная кнопка.')
        return
    res = await new_claim(user.id, item_id)
    if res == 'ok':
        await callback.message.answer('Заявка создана (pending).')
    elif res == 'already':
        await callback.message.answer('Вы уже подавали заявку на эту вещь.')
    elif res == 'no_item':
        await callback.message.answer('Вещь не найдена (устаревшая кнопка).')
    elif res == 'returned':
        await callback.message.answer('Вещь уже возвращена.')
    elif res == 'own':
        await callback.message.answer('Нельзя подать заявку на собственную вещь.')
    else:
        await callback.message.answer('Вещь не найдена (устаревшая кнопка).')

@router.callback_query(F.data.startswith('claim:approve:'))
async def ok_claim(callback: CallbackQuery):
    await callback.answer()
    user = callback.from_user
    claim_id = get_id(callback.data, 'claim:approve:')
    if claim_id is None:
        await callback.message.answer('Некорректная кнопка.')
        return
    res = await approve_claim(claim_id, user.id)
    if res == 'ok':
        await callback.message.answer('Вещь передана.')
    elif res == 'no_claim':
        await callback.message.answer('Заявка не найдена (устаревшая кнопка).')
    elif res == 'no_item':
        await callback.message.answer('Вещь не найдена.')
    elif res == 'not_owner':
        await callback.message.answer('Вы не являетесь владельцем этой вещи.')
    elif res == 'returned':
        await callback.message.answer('Вещь уже передана. Повторная передача невозможна.')
    elif res == 'done':
        await callback.message.answer('Заявка уже обработана.')
    else:
        await callback.message.answer('Заявка не найдена (устаревшая кнопка).')
