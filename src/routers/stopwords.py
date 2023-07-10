from traceback import format_exc

from aiogram import Router, types, filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton

import config
from db import db

router = Router()


class StopWordsState(StatesGroup):
    user_input = State()
    delete = State()


@router.callback_query(filters.Text('stop_words'))
async def keywords(callback: types.CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Добавить слово 📥', callback_data='add_stop_word'), InlineKeyboardButton(text='Удалить слово 🗑', callback_data='delete_stop_word')],
            [InlineKeyboardButton(text='Список слов 📋', callback_data='stop_word_list')],
            [InlineKeyboardButton(text='◀️ Назад', callback_data='menu')]
    ])
    await callback.message.answer('🔴 Меню стов-слов, которые будут искаться в сообщениях.', reply_markup=markup)


@router.callback_query(filters.Text('add_stop_word'))
async def add_stop_word(callback: types.CallbackQuery, state: FSMContext):
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='❌ Отмена')]], resize_keyboard=True)
    await callback.message.answer('🔴 Укажите стоп-слово (можно несколько через запятую)', reply_markup=markup)
    await state.set_state(StopWordsState.user_input)


@router.message(StopWordsState.user_input)
async def user_input(message: types.Message, state: FSMContext):
    try:
        msg = '✅ Успешно добавлено'
        for stop_word in message.text.split('\n'):
            if stop_word == '❌ Отмена':
                msg = 'Возвращаемся назад.'
                break
            if stop_word in config.stop_words:
                await message.answer(f'Стоп-слово <b>{stop_word}</b> уже добавлено.', parse_mode='html')
                continue
            config.stop_words.append(stop_word.strip().lower())
            db.create('stop_words', stop_word.strip().lower())
        await message.answer(msg, reply_markup=ReplyKeyboardRemove())
    except:
        await message.answer('❌ Ошибка при добавлении', reply_markup=ReplyKeyboardRemove())
        print(format_exc())
    finally:
        await state.clear()
        markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Добавить слово 📥', callback_data='add_stop_word'), InlineKeyboardButton(text='Удалить слово 🗑', callback_data='delete_stop_word')],
                [InlineKeyboardButton(text='Список слов 📋', callback_data='stop_word_list')],
                [InlineKeyboardButton(text='◀️ Назад', callback_data='menu')]
        ])
        await message.answer('🔴 Меню стов-слов, которые будут искаться в сообщениях.', reply_markup=markup)


@router.callback_query(filters.Text('stop_word_list'))
async def stop_word_list(callback: types.CallbackQuery):
    msg = '🔴 Список стоп-слов:\n\n'

    for index, stop_word in enumerate(config.stop_words):
        msg += f'{index+1}. {stop_word}\n'
     
    if (not len(config.stop_words)):
        msg += 'Список пуст.'

    await callback.message.answer(msg)


@router.callback_query(filters.Text('delete_stop_word'))
async def delete_stop_word(callback: types.CallbackQuery, state: FSMContext):
    msg = '🗑 Укажите номер слова, которое нужно удалить (можно несколько, через запятую)\n\n'

    for index, stop_word in enumerate(config.stop_words):
        msg += f'{index+1}. {stop_word}\n'
     
    if (not len(config.stop_words)):
        await callback.message.answer('Нет слов для удаления.')
        return
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='❌ Отмена')]], resize_keyboard=True)
    await callback.message.answer(msg, reply_markup=markup)
    await state.set_state(StopWordsState.delete)


@router.message(StopWordsState.delete)
async def delete(message: types.Message, state: FSMContext):
    try:
        msg = '✅ Успешно удалено'
        values = message.text.split('\n')
        for value in values:
            if value.strip() == '❌ Отмена':
                msg = 'Возвращаемся назад.'
                break
            if value.strip() not in config.stop_words:
                await message.answer(f'Стоп-слово <b>{value.strip()}</b> отсутствует', parse_mode='html')
                continue
            config.stop_words.remove(value)
            db.delete('stop_words', 'word', value)
        await message.answer(msg, reply_markup=ReplyKeyboardRemove())
    except:
        await message.answer('❌ Ошибка при удалении', reply_markup=ReplyKeyboardRemove())
        print(format_exc())
    finally:
        await state.clear()
        markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Добавить слово 📥', callback_data='add_stop_word'), InlineKeyboardButton(text='Удалить слово 🗑', callback_data='delete_stop_word')],
                [InlineKeyboardButton(text='Список слов 📋', callback_data='stop_word_list')],
                [InlineKeyboardButton(text='◀️ Назад', callback_data='menu')]
        ])
        await message.answer('🔴 Меню стов-слов, которые будут искаться в сообщениях.', reply_markup=markup)
