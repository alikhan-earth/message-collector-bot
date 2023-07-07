from traceback import format_exc

from aiogram import Router, types, filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
from db import db

router = Router()


class ChatsState(StatesGroup):
    user_input = State()
    delete = State()


@router.callback_query(filters.Text('chats'))
async def keywords(callback: types.CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Добавить чат 📥', callback_data='add_chat'), InlineKeyboardButton(text='Удалить чат 🗑', callback_data='delete_chat')],
            [InlineKeyboardButton(text='Список чатов 📋', callback_data='chat_list')],
            [InlineKeyboardButton(text='◀️ Назад', callback_data='menu')]
    ])
    await callback.message.edit_text('🗂️ Меню чатов.')
    await callback.message.edit_reply_markup(callback.inline_message_id, markup)


@router.callback_query(filters.Text('add_chat'))
async def add_chat(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('🗂️ Укажите чат (ссылка или ID).\nМожно несколько через запятую.')
    await state.set_state(ChatsState.user_input)


@router.message(ChatsState.user_input)
async def user_input(message: types.Message, state: FSMContext):
    try:
        for chat in message.text.lower().split(','):
            config.chats.append(chat.replace('http://t.me', '').replace('https://t.me', '').replace('/', '').replace('@', '').strip())
            db.create('chats', chat.replace('http://t.me', '').replace('https://t.me', '').replace('/', '').replace('@', '').strip())
        await message.answer('✅ Успешно добавлено')
    except:
        await message.answer('❌ Ошибка при добавлении')
        print(format_exc())
    finally:
        await state.clear()


@router.callback_query(filters.Text('chat_list'))
async def chat_list(callback: types.CallbackQuery):
    msg = '🗂️ Список чатов:\n\n'

    for index, chat in enumerate(config.chats):
        msg += f"""{index+1}. <a href="http://t.me/{chat}">{chat}</a>\n"""
     
    if (not len(config.chats)):
        msg += 'Список пуст.'

    await callback.message.answer(msg, 'html', disable_web_page_preview=True)


@router.callback_query(filters.Text('delete_chat'))
async def delete_chat(callback: types.CallbackQuery, state: FSMContext):
    msg = '🗑 Укажите номер чата, который нужно удалить (можно несколько, через запятую)\n\n'

    for index, chat in enumerate(config.chats):
        msg += f"""{index+1}. <a href="http://t.me/{chat}">{chat}</a>\n"""
    
    if (not len(config.chats)):
        await callback.message.answer('Нет чатов для удаления.')
        return

    await callback.message.answer(msg, 'html', disable_web_page_preview=True)
    await state.set_state(ChatsState.delete)


@router.message(ChatsState.delete)
async def delete(message: types.Message, state: FSMContext):
    try:
        values = [config.chats[int(index)-1] for index in message.text.split(',')]
        for value in values:
            config.chats.remove(value)
            db.delete('chats', 'chat_id', value)
        await message.answer('✅ Успешно удалено')
    except:
        await message.answer('❌ Ошибка при удалении')
        print(format_exc())
    finally:
        await state.clear()
