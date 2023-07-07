from traceback import format_exc

from aiogram import Router, types, filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import config
from db import db

router = Router()


class MonitoringChatsState(StatesGroup):
    user_input = State()
    delete = State()


@router.callback_query(filters.Text('monitoring_chats'))
async def keywords(callback: types.CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Добавить чат 📥', callback_data='add_monitoring_chat'), InlineKeyboardButton(text='Удалить чат 🗑', callback_data='delete_monitoring_chat')],
            [InlineKeyboardButton(text='Список чатов 📋', callback_data='monitoring_chat_list')],
            [InlineKeyboardButton(text='◀️ Назад', callback_data='menu')]
    ])
    await callback.message.edit_text('🗂️ Меню чатов для мониторинга.')
    await callback.message.edit_reply_markup(callback.inline_message_id, markup)


@router.callback_query(filters.Text('add_monitoring_chat'))
async def add_monitoring_chat(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('🗂️ Укажите чат (ссылка или ID).\nМожно несколько через запятую.')
    await state.set_state(MonitoringChatsState.user_input)


@router.message(MonitoringChatsState.user_input)
async def user_input(message: types.Message, state: FSMContext):
    try:
        for monitoring_chat in message.text.lower().split(','):
            config.monitoring_chats.append(monitoring_chat.replace('http://t.me', '').replace('https://t.me', '').replace('/', '').replace('@', '').strip())
            db.create('monitoring_chats', monitoring_chat.replace('http://t.me', '').replace('https://t.me', '').replace('/', '').replace('@', '').strip())
        await message.answer('✅ Успешно добавлено')
    except:
        await message.answer('❌ Ошибка при добавлении')
        print(format_exc())
    finally:
        await state.clear()


@router.callback_query(filters.Text('monitoring_chat_list'))
async def monitoring_chat_list(callback: types.CallbackQuery):
    msg = '🗂️ Список чатов для мониторинга:\n\n'

    for index, monitoring_chat in enumerate(config.monitoring_chats):
        msg += f"""{index+1}. <a href="http://t.me/{monitoring_chat}">{monitoring_chat}</a>\n"""
     
    if (not len(config.monitoring_chats)):
        msg += 'Список пуст.'

    await callback.message.answer(msg, 'html', disable_web_page_preview=True)


@router.callback_query(filters.Text('delete_monitoring_chat'))
async def delete_monitoring_chat(callback: types.CallbackQuery, state: FSMContext):
    msg = '🗑 Укажите номер чата, который нужно удалить (можно несколько, через запятую)\n\n'

    for index, monitoring_chat in enumerate(config.monitoring_chats):
        msg += f"""{index+1}. <a href="http://t.me/{monitoring_chat}">{monitoring_chat}</a>\n"""
     
    if (not len(config.monitoring_chats)):
        await callback.message.answer('Нет чатов для удаления.')
        return

    await callback.message.answer(msg, 'html', disable_web_page_preview=True)
    await state.set_state(MonitoringChatsState.delete)


@router.message(MonitoringChatsState.delete)
async def delete(message: types.Message, state: FSMContext):
    try:
        values = [config.monitoring_chats[int(index)-1] for index in message.text.split(',')]
        for value in values:
            config.monitoring_chats.remove(value)
            db.delete('monitoring_chats', 'chat_id', value)
        await message.answer('✅ Успешно удалено')
    except:
        await message.answer('❌ Ошибка при удалении')
        print(format_exc())
    finally:
        await state.clear()
