from traceback import format_exc
import asyncio
from random import randint

from aiogram import Router, types, filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

import config
from db import db

router = Router()
to_append_chats = []

class MonitoringChatsState(StatesGroup):
    user_input = State()
    delete = State()


def check_chat(chat):
    if chat[chat.rindex('/')+1] == '+':
        return chat
    if 'AAAAA' in chat and 'joinchat' in chat:
        return chat
    return chat.replace('http://t.me', '').replace('https://t.me', '').replace('/', '').replace('@', '').strip()
    

@router.callback_query(filters.Text('monitoring_chats'))
async def keywords(callback: types.CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Добавить чат 📥', callback_data='add_monitoring_chat'), InlineKeyboardButton(text='Удалить чат 🗑', callback_data='delete_monitoring_chat')],
            [InlineKeyboardButton(text='Список чатов 📋', callback_data='monitoring_chat_list')],
            [InlineKeyboardButton(text='◀️ Назад', callback_data='menu')]
    ])
    await callback.message.answer('🗂️ Меню чатов для мониторинга.', reply_markup=markup)


@router.callback_query(filters.Text('add_monitoring_chat'))
async def add_monitoring_chat(callback: types.CallbackQuery, state: FSMContext):
    reply_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='❌ Отмена')]], resize_keyboard=True)
    await callback.message.answer('🗂️ Укажите чаты (ссылка или ID).', reply_markup=reply_markup)
    await state.set_state(MonitoringChatsState.user_input)


@router.message(MonitoringChatsState.user_input)
async def user_input(message: types.Message, state: FSMContext):
    global to_append_chats

    try:
        msg = '✅ Успешно добавлено'
        for monitoring_chat in map(check_chat, message.text.split('\n')):
            if monitoring_chat.strip() == '❌ Отмена':
                msg = 'Возвращаемся назад'
                break
            if monitoring_chat.strip() in config.monitoring_chats or monitoring_chat in to_append_chats:
                await message.answer(f"""Чат <a href="{'http://t.me/' + monitoring_chat if 'joinchat' not in monitoring_chat else monitoring_chat}"><b>{monitoring_chat.strip()}</b></a> уже добавлен.""", parse_mode='html')
                continue
            to_append_chats.append(monitoring_chat)
        await message.answer(msg, parse_mode='html', reply_markup=ReplyKeyboardRemove())
    except:
        await message.answer('❌ Ошибка при добавлении', reply_markup=ReplyKeyboardRemove())
        print(format_exc())
    finally:
        await state.clear()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Добавить чат 📥', callback_data='add_monitoring_chat'), InlineKeyboardButton(text='Удалить чат 🗑', callback_data='delete_monitoring_chat')],
            [InlineKeyboardButton(text='Список чатов 📋', callback_data='monitoring_chat_list')],
            [InlineKeyboardButton(text='◀️ Назад', callback_data='menu')]
        ])
        await message.answer('🗂️ Меню чатов для мониторинга.', reply_markup=markup)
        print('to_append_chats', to_append_chats)
        to_append_chats_backup = to_append_chats[:]
        for chat in to_append_chats_backup:
            if chat in to_append_chats:
                config.monitoring_chats.append(chat)
                db.create('monitoring_chats', chat)
                to_append_chats.remove(chat)
                await asyncio.sleep(randint(480, 600))

@router.callback_query(filters.Text('monitoring_chat_list'))
async def monitoring_chat_list(callback: types.CallbackQuery):
    msg = '🗂️ Список чатов для мониторинга:\n\n'
    last_index = 0
    for index, monitoring_chat in enumerate(config.monitoring_chats):
        msg += f"""{index+1}. <a href="{'http://t.me/' + monitoring_chat if 'joinchat' not in monitoring_chat else monitoring_chat}">{monitoring_chat}</a>\n"""
        last_index = index + 1

    for index, to_append_chat in enumerate(to_append_chats):
        msg += f"""{last_index+index+1}. <a href="{'http://t.me/' + monitoring_chat if 'joinchat' not in monitoring_chat else monitoring_chat}">{to_append_chat}</a> (ожидает добавления)\n"""


    if (not len(config.monitoring_chats + to_append_chats)):
        msg += 'Список пуст.'

    await callback.message.answer(msg, 'html', disable_web_page_preview=True)


@router.callback_query(filters.Text('delete_monitoring_chat'))
async def delete_monitoring_chat(callback: types.CallbackQuery, state: FSMContext):
    msg = '🗑 Укажите чаты, которые нужно удалить\n\n'
    last_index = 0
    for index, monitoring_chat in enumerate(config.monitoring_chats):
        msg += f"""{index+1}. <a href="{'http://t.me/' + monitoring_chat if 'joinchat' not in monitoring_chat else monitoring_chat}">{monitoring_chat}</a>\n"""
        last_index = index+1
    
    for index, to_append_chat in enumerate(to_append_chats):
        msg += f"""{last_index+index+1}. <a href="{'http://t.me/' + monitoring_chat if 'joinchat' not in monitoring_chat else monitoring_chat}">{to_append_chat}</a> (ожидает добавления)\n"""

    if (not len(config.monitoring_chats + to_append_chats)):
        await callback.message.answer('Нет чатов для удаления.')
        return
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='❌ Отмена')]], resize_keyboard=True)
    await callback.message.answer(msg, 'html', disable_web_page_preview=True, reply_markup=markup)
    await state.set_state(MonitoringChatsState.delete)


@router.message(MonitoringChatsState.delete)
async def delete(message: types.Message, state: FSMContext):
    msg = '✅ Успешно удалено'
    try:
        values = map(check_chat, message.text.split('\n'))
        for value in values:
            if value.strip() == '❌ Отмена':
                msg = 'Возвращаемся назад.'
                break
            if value.strip() in to_append_chats:
                to_append_chats.remove(value.strip())
                continue
            if value.strip() not in config.monitoring_chats:
                await message.answer(f"""Чат <a href="{'http://t.me/' + value if 'joinchat' not in value else value}"><b>{value.strip()}</b></a> отсутствует""", parse_mode='html')
                continue
            config.monitoring_chats.remove(value)
            db.delete('monitoring_chats', 'chat_id', value)
    except:
        msg = '❌ Ошибка при удалении'
        print(format_exc())
    finally:
        await message.answer(msg, reply_markup=ReplyKeyboardRemove())
        await state.clear()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Добавить чат 📥', callback_data='add_monitoring_chat'), InlineKeyboardButton(text='Удалить чат 🗑', callback_data='delete_monitoring_chat')],
            [InlineKeyboardButton(text='Список чатов 📋', callback_data='monitoring_chat_list')],
            [InlineKeyboardButton(text='◀️ Назад', callback_data='menu')]
        ])
        await message.answer('🗂️ Меню чатов для мониторинга.', reply_markup=markup)
