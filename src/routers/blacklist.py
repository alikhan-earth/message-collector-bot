from traceback import format_exc

from aiogram import Router, types, filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

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
    await callback.message.answer('🚷 Меню пользователей, сообщения которых будут игнорироваться.', reply_markup=markup)


@router.callback_query(filters.Text('add_black_list'))
async def add_black_list(callback: types.CallbackQuery, state: FSMContext):
    reply_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='❌ Отмена')]], resize_keyboard=True)
    await callback.message.answer('🚷 Укажите пользователя (ссылка или ID).\nМожно несколько через запятую.', reply_markup=reply_markup)
    await state.set_state(BlackListState.user_input)


@router.message(BlackListState.user_input)
async def user_input(message: types.Message, state: FSMContext):
    try:
        msg = '✅ Успешно добавлено'
        for user_id in map(lambda user_id: user_id.replace('http://t.me', '').replace('https://t.me', '').replace('/', '').replace('@', '').strip(), message.text.split('\n')):
            if user_id.strip() == '❌ Отмена':
                msg = 'Возвращаемся назад'
                break
            if user_id.strip() in config.monitoring_chats:
                await message.answer(f'Пользователь <a href="http://t.me/{user_id}"><b>{user_id.strip()}</b></a> уже находится в ЧС.', parse_mode='html')
                continue
            config.black_list.append(user_id)
            db.create('black_list', user_id)
        await message.answer(msg, reply_markup=ReplyKeyboardRemove())
    except:
        await message.answer('❌ Ошибка при добавлении', reply_markup=ReplyKeyboardRemove())
        print(format_exc())
    finally:
        await state.clear()
        markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Добавить пользователя 📥', callback_data='add_black_list'), InlineKeyboardButton(text='Удалить пользователя 🗑', callback_data='delete_black_list')],
                [InlineKeyboardButton(text='Список пользователей 📋', callback_data='black_list_list')],
                [InlineKeyboardButton(text='◀️ Назад', callback_data='menu')]
        ])
        await message.answer('🚷 Меню пользователей, сообщения которых будут игнорироваться.', reply_markup=markup)


@router.callback_query(filters.Text('black_list_list'))
async def black_list_list(callback: types.CallbackQuery):
    msgs = ['🚷 Черный список:\n\n']

    for index, user_id in enumerate(config.black_list):
        if len(msgs[-1]) < 2250:
            msgs[-1] += f"""{index+1}. <a href="http://t.me/{user_id}">{user_id}</a>\n"""
        else:
            msgs.append('')
            msgs[-1] += f"""{index+1}. <a href="http://t.me/{user_id}">{user_id}</a>\n"""
     
    if (not len(config.black_list)):
        msgs[-1] += 'Список пуст.'

    for msg in msgs:
        await callback.message.answer(msg, 'html', disable_web_page_preview=True)


@router.callback_query(filters.Text('delete_black_list'))
async def delete_key_word(callback: types.CallbackQuery, state: FSMContext):
    msgs = ['🗑 Укажите номер пользователя, которого нужно удалить (можно несколько, через запятую)\n\n']

    for index, user_id in enumerate(config.black_list):
        if len(msgs[-1]) < 2250:
            msgs[-1] += f"""{index+1}. <a href="http://t.me/{user_id}">{user_id}</a>\n"""
        else:
            msgs.append('')
            msgs[-1] += f"""{index+1}. <a href="http://t.me/{user_id}">{user_id}</a>\n"""
     
    if (not len(config.black_list)):
        await callback.message.answer('Нет пользователей для удаления.')
        return
    reply_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='❌ Отмена')]], resize_keyboard=True)
    for msg in msgs:
        await callback.message.answer(msg, 'html', disable_web_page_preview=True, reply_markup=reply_markup)
    await state.set_state(BlackListState.delete)


@router.message(BlackListState.delete)
async def delete(message: types.Message, state: FSMContext):
    try:
        msg = '✅ Успешно удалено'
        values = map(lambda user_id: user_id.replace('http://t.me', '').replace('https://t.me', '').replace('/', '').replace('@', '').strip(), message.text.split('\n'))
        for value in values:
            if value.strip() == '❌ Отмена':
                msg = 'Возвращаемся назад'
                break
            if value.strip() not in config.black_list:
                await message.answer(f'Пользователь <a href="http://t.me/{value}"><b>{value.strip()}</b></a> отсутсвует в ЧС.', parse_mode='html')
                continue
            config.black_list.remove(value)
            db.delete('black_list', 'user_id', value)
        await message.answer(msg, reply_markup=ReplyKeyboardRemove())
    except:
        await message.answer('❌ Ошибка при удалении', reply_markup=ReplyKeyboardRemove())
        print(format_exc())
    finally:
        await state.clear()
        markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Добавить пользователя 📥', callback_data='add_black_list'), InlineKeyboardButton(text='Удалить пользователя 🗑', callback_data='delete_black_list')],
                [InlineKeyboardButton(text='Список пользователей 📋', callback_data='black_list_list')],
                [InlineKeyboardButton(text='◀️ Назад', callback_data='menu')]
        ])
        await message.answer('🚷 Меню пользователей, сообщения которых будут игнорироваться.', reply_markup=markup)
