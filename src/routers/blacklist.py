from traceback import format_exc

from aiogram import Router, types, filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
from db import db

router = Router()


class BlackListState(StatesGroup):
    user_input = State()
    delete = State()


@router.callback_query(filters.Text('black_list'))
async def blacklist(callback: types.CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Добавить пользователя 📥', callback_data='add_black_list'), InlineKeyboardButton(text='Удалить пользователя 🗑', callback_data='delete_black_list')],
            [InlineKeyboardButton(text='Список пользователей 📋', callback_data='black_list_list')],
            [InlineKeyboardButton(text='◀️ Назад', callback_data='menu')]
    ])
    await callback.message.edit_text('🚷 Меню пользователей, сообщения которых будут игнорироваться.')
    await callback.message.edit_reply_markup(callback.inline_message_id, markup)


@router.callback_query(filters.Text('add_black_list'))
async def add_black_list(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('🚷 Укажите пользователя (Ссылка или ID).\nМожно несколько через запятую.')
    await state.set_state(BlackListState.user_input)


@router.message(BlackListState.user_input)
async def user_input(message: types.Message, state: FSMContext):
    try:
        for user_id in message.text.lower().split(','):
            config.black_list.append(user_id.replace('http://t.me', '').replace('https://t.me', '').replace('/', '').replace('@', '').strip())
            db.create('black_list', user_id.replace('http://t.me', '').replace('https://t.me', '').replace('/', '').replace('@', '').strip())
        await message.answer('✅ Успешно добавлено')
    except:
        await message.answer('❌ Ошибка при добавлении')
        print(format_exc())
    finally:
        await state.clear()


@router.callback_query(filters.Text('black_list_list'))
async def black_list_list(callback: types.CallbackQuery):
    msg = '🚷 Черный список:\n\n'

    for index, user_id in enumerate(config.black_list):
        msg += f"""{index+1}. <a href="http://t.me/{user_id}">{user_id}</a>\n"""
     
    if (not len(config.black_list)):
        msg += 'Список пуст.'

    await callback.message.answer(msg, 'html', disable_web_page_preview=True)


@router.callback_query(filters.Text('delete_black_list'))
async def delete_key_word(callback: types.CallbackQuery, state: FSMContext):
    msg = '🗑 Укажите номер пользователя, которого нужно удалить (можно несколько, через запятую)\n\n'

    for index, user_id in enumerate(config.black_list):
        msg += f"""{index+1}. <a href="http://t.me/{user_id}">{user_id}</a>\n"""
     
    if (not len(config.black_list)):
        await callback.message.answer('Нет пользователей для удаления.')
        return

    await callback.message.answer(msg, 'html', disable_web_page_preview=True)
    await state.set_state(BlackListState.delete)


@router.message(BlackListState.delete)
async def delete(message: types.Message, state: FSMContext):
    try:
        values = [config.black_list[int(index)-1] for index in message.text.split(',')]
        for value in values:
            config.black_list.remove(value)
            db.delete('black_list', 'user_id', value)
        await message.answer('✅ Успешно удалено')
    except:
        await message.answer('❌ Ошибка при удалении')
        print(format_exc())
    finally:
        await state.clear()
