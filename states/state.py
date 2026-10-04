from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from board import *
from service import *
from states.states import AddItem, ShowItem, ShowClaims

router = Router()

def check_id(text):
    try:
        value = int(text.strip().split()[0])
    except Exception:
        return None
    if value <= 0:
        return None
    return value

def item_text(item):
    return f"🔹 {item['title']}\n\nОписание: {item['description']}\n📍 Место: {item['location']}"

@router.message(F.text == '❌ Отмена')
async def cancel_btn(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Ввод отменён.', reply_markup=main())

@router.message(Command('add_item'))
@router.message(F.text == '➕ Добавить')
async def add_one(message: Message, state: FSMContext):
    await state.set_state(AddItem.title)
    await message.answer('Шаг 1/4. Введите название предмета:', reply_markup=cancel())

@router.message(AddItem.title, F.text, ~F.text.startswith('/'))
async def title_step(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text:
        await message.answer('Пусто. Попробуйте ещё раз:', reply_markup=cancel())
        return
    await state.update_data(title=text)
    await state.set_state(AddItem.description)
    await message.answer('Шаг 2/4. Введите описание предмета:', reply_markup=cancel())

@router.message(AddItem.description, F.text, ~F.text.startswith('/'))
async def desc_step(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text:
        await message.answer('Пусто. Попробуйте ещё раз:', reply_markup=cancel())
        return
    await state.update_data(description=text)
    await state.set_state(AddItem.location)
    await message.answer('Шаг 3/4. Введите место находки:', reply_markup=cancel())

@router.message(AddItem.location, F.text, ~F.text.startswith('/'))
async def loc_step(message: Message, state: FSMContext):
    text = message.text.strip()
    if not text:
        await message.answer('Пусто. Попробуйте ещё раз:', reply_markup=cancel())
        return
    await state.update_data(location=text)
    await state.set_state(AddItem.photo)
    await message.answer('Шаг 4/4. Отправьте фото предмета:', reply_markup=cancel())

@router.message(AddItem.photo, F.photo)
async def photo_step(message: Message, state: FSMContext):
    user = message.from_user
    data = await state.get_data()
    row = await save_item(user.id, data["title"], data["description"], data["location"], message.photo[-1].file_id)
    await state.clear()
    if row is None:
        await message.answer('Ошибка! Попробуйте ещё раз /add_item', reply_markup=main())
        return
    await message.answer(f"Вещь сохранена! Item ID: {row['id']}", reply_markup=main())

@router.message(AddItem.photo)
async def photo_bad(message: Message, state: FSMContext):
    if message.text == '/cancel' or message.text == '❌ Отмена':
        await state.clear()
        await message.answer('Ввод отменён.', reply_markup=main())
        return
    if message.text and message.text.startswith('/'):
        return
    await message.answer('Пожалуйста, отправьте фото предмета:', reply_markup=cancel())

@router.message(Command('item'))
async def one_item(message: Message, state: FSMContext):
    await state.set_state(ShowItem.item_id)
    await message.answer('Введите ID вещи:', reply_markup=cancel())

@router.message(ShowItem.item_id, F.text, ~F.text.startswith('/'))
async def one_item_id(message: Message, state: FSMContext):
    item_id = check_id(message.text)
    if item_id is None:
        await message.answer('id должен быть числом больше 0. Попробуйте ещё раз:', reply_markup=cancel())
        return
    item = await get_item(item_id)
    await state.clear()
    if item is None:
        await message.answer('Вещь не найдена.', reply_markup=main())
        return
    await message.answer_photo(photo=item['photo_file_id'], caption=item_text(item), reply_markup=item_board(item['id']))

@router.message(Command('claims'))
async def owners_list(message: Message, state: FSMContext):
    await state.set_state(ShowClaims.item_id)
    await message.answer('Введите ID твоей вещи:', reply_markup=cancel())

@router.message(ShowClaims.item_id, F.text, ~F.text.startswith('/'))
async def owners_list_id(message: Message, state: FSMContext):
    user = message.from_user
    item_id = check_id(message.text)
    if item_id is None:
        await message.answer('id должен быть числом больше 0. Попробуйте ещё раз:', reply_markup=cancel())
        return
    item = await get_item(item_id)
    if item is None:
        await state.clear()
        await message.answer('Вещь не найдена.', reply_markup=main())
        return
    if int(item['owner_id']) != int(user.id):
        await state.clear()
        await message.answer('Вы не являетесь владельцем этой вещи.', reply_markup=main())
        return
    rows = await pending_claims(item_id)
    await state.clear()
    if not rows:
        await message.answer('Нет pending заявок на эту вещь.', reply_markup=main())
        return
    text = f"Заявки на вещь «{item['title']}»:\n\n"
    for i in rows:
        text += f"Заявка №{i['id']} от пользователя {i['user_id']} — {i['status']}\n"
    await message.answer(text, reply_markup=claims_board(rows))

@router.message(Command('cancel'))
async def cancel_one(message: Message, state: FSMContext):
    cur = await state.get_state()
    if cur is None:
        await message.answer('Нет активного ввода.', reply_markup=main())
    else:
        await state.clear()
        await message.answer('Ввод отменён.', reply_markup=main())
