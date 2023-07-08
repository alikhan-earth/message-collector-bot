from traceback import format_exc
import asyncio
from random import randint

from aiogram import Router, types, filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

import config
from db import db

router = Router()
to_append_chats = []

class ChatsState(StatesGroup):
    user_input = State()
    delete = State()


@router.callback_query(filters.Text('chats'))
async def keywords(callback: types.CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Добавить чат 📥', callback_data='add_chat'), InlineKeyboardButton(text='Удалить чат 🗑', callback_data='delete_chat')],
            [InlineKeyboardButton(text='Список чатов 📋', callback_data='chat_list')],
            [InlineKeyboardButton(text='◀️ Назад', callback_data='chats_settings')]
    ])
    await callback.message.answer('🗂️ Меню чатов.', reply_markup=markup)


@router.callback_query(filters.Text('add_chat'))
async def add_chat(callback: types.CallbackQuery, state: FSMContext):
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='❌ Отмена')]], resize_keyboard=True)
    await callback.message.answer('🗂️ Укажите чат (ссылка или ID).\nМожно несколько через запятую.', reply_markup=markup)
    await state.set_state(ChatsState.user_input)


@router.message(ChatsState.user_input)
async def user_input(message: types.Message, state: FSMContext):
    global to_append_chats

    try:
        msg = '✅ Успешно добавлено'
        for chat in map(lambda chat: chat.replace('http://t.me', '').replace('https://t.me', '').replace('/', '').replace('@', '').strip(), message.text.lower().split('\n')):
            if chat == '❌ Отмена':
                msg = 'Возвращаемся назад.'
                break
            if chat in config.chats or chat in to_append_chats:
                await message.answer(f'Чат <a href="http://t.me/{chat.strip()}"><b>{chat.strip()}</b></a> уже добавлен.', parse_mode='html')
                continue
            to_append_chats.append(chat.replace('http://t.me', '').replace('https://t.me', '').replace('/', '').replace('@', '').strip())
        await message.answer(msg, reply_markup=ReplyKeyboardRemove())
    except:
        await message.answer('❌ Ошибка при добавлении', reply_markup=ReplyKeyboardRemove())
        print(format_exc())
    finally:
        await state.clear()
        markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Добавить чат 📥', callback_data='add_chat'), InlineKeyboardButton(text='Удалить чат 🗑', callback_data='delete_chat')],
                [InlineKeyboardButton(text='Список чатов 📋', callback_data='chat_list')],
                [InlineKeyboardButton(text='◀️ Назад', callback_data='chats_settings')]
        ])
        await message.answer('🗂️ Меню чатов.', reply_markup=markup)
        to_append_chats_backup = to_append_chats[:]
        for chat in to_append_chats_backup:
            if chat in to_append_chats:
                config.chats.append(chat)
                db.create('chats', chat)
                to_append_chats.remove(chat)
                await asyncio.sleep(randint(480, 600))

@router.callback_query(filters.Text('chat_list'))
async def chat_list(callback: types.CallbackQuery):
    msg = '🗂️ Список чатов:\n\n'
    last_index = 0
    for index, chat in enumerate(config.chats):
        msg += f"""{index+1}. <a href="http://t.me/{chat}">{chat}</a>\n"""
        last_index = index + 1

    for index, to_append_chat in enumerate(to_append_chats):
        msg += f"""{last_index+index+1}. <a href="http://t.me/{to_append_chat}">{to_append_chat}</a> (ожидает добавления)\n"""
     
    if (not len(config.chats + to_append_chats)):
        msg += 'Список пуст.'

    await callback.message.answer(msg, 'html', disable_web_page_preview=True)


@router.callback_query(filters.Text('delete_chat'))
async def delete_chat(callback: types.CallbackQuery, state: FSMContext):
    msg = '🗑 Укажите номер чата, который нужно удалить (можно несколько, через запятую)\n\n'
    last_index = 0
    for index, chat in enumerate(config.chats):
        msg += f"""{index+1}. <a href="http://t.me/{chat}">{chat}</a>\n"""
        last_index = index+1
    
    for index, to_append_chat in enumerate(to_append_chats):
        msg += f"""{last_index+index+1}. <a href="http://t.me/{to_append_chat}">{to_append_chat}</a> (ожидает добавления)\n"""

    if (not len(config.chats + to_append_chats)):
        await callback.message.answer('Нет чатов для удаления.')
        return

    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='❌ Отмена')]], resize_keyboard=True)
    await callback.message.answer(msg, 'html', disable_web_page_preview=True, reply_markup=markup)
    await state.set_state(ChatsState.delete)


@router.message(ChatsState.delete)
async def delete(message: types.Message, state: FSMContext):
    try:
        msg = '✅ Успешно удалено'
        values = map(lambda chat: chat.replace('http://t.me', '').replace('https://t.me', '').replace('/', '').replace('@', '').strip(), message.text.split('\n'))
        for value in values:
            if value.strip() == '❌ Отмена':
                msg = 'Возвращаемся назад.'
                break
            if value.strip() in to_append_chats:
                to_append_chats.remove(value.strip())
                continue
            if value.strip() not in config.chats:
                await message.answer(f'Чат <a href="http://t.me/{value.strip()}"><b>{value.strip()}</b></a> отсутствует', parse_mode='html')
                continue
            config.chats.remove(value)
            db.delete('chats', 'chat_id', value)
        await message.answer(msg, reply_markup=ReplyKeyboardRemove())
    except:
        await message.answer('❌ Ошибка при удалении', reply_markup=ReplyKeyboardRemove())
        print(format_exc())
    finally:
        await state.clear()
        markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Добавить чат 📥', callback_data='add_chat'), InlineKeyboardButton(text='Удалить чат 🗑', callback_data='delete_chat')],
                [InlineKeyboardButton(text='Список чатов 📋', callback_data='chat_list')],
                [InlineKeyboardButton(text='◀️ Назад', callback_data='chats_settings')]
        ])
        await message.answer('🗂️ Меню чатов.', reply_markup=markup)