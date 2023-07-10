from traceback import format_exc

from aiogram import Router, types, filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

import config
from db import db

router = Router()


class KeyWordsState(StatesGroup):
    user_input = State()
    delete = State()


@router.callback_query(filters.Text('key_words'))
async def keywords(callback: types.CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Добавить слово 📥', callback_data='add_key_word'), InlineKeyboardButton(text='Удалить слово 🗑', callback_data='delete_key_word')],
            [InlineKeyboardButton(text='Список слов 📋', callback_data='key_word_list')],
            [InlineKeyboardButton(text='◀️ Назад', callback_data='menu')]
    ])
    await callback.message.answer('🔑 Меню ключевых слов, которые будут искаться в сообщениях.', reply_markup=markup)


@router.callback_query(filters.Text('add_key_word'))
async def add_key_word(callback: types.CallbackQuery, state: FSMContext):
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='❌ Отмена')]], resize_keyboard=True)
    await callback.message.answer('🔑 Укажите ключевое слово (можно несколько через запятую)', reply_markup=markup)
    await state.set_state(KeyWordsState.user_input)


@router.message(KeyWordsState.user_input)
async def user_input(message: types.Message, state: FSMContext):
    try:
        msg = '✅ Успешно добавлено'
        for key_word in message.text.split('\n'):
            if key_word == '❌ Отмена':
                msg = 'Возвращаемся назад.'
                break
            if key_word.lower() in config.key_words:
                await message.answer(f'Ключевое слово <b>{key_word}</b> уже добавлено.', parse_mode='html')
                continue
            config.key_words.append(key_word.strip().lower())
            db.create('key_words', key_word.strip().lower())
        await message.answer(msg, reply_markup=ReplyKeyboardRemove())
    except:
        await message.answer('❌ Ошибка при добавлении', reply_markup=ReplyKeyboardRemove())
        print(format_exc())
    finally:
        await state.clear()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Добавить слово 📥', callback_data='add_key_word'), InlineKeyboardButton(text='Удалить слово 🗑', callback_data='delete_key_word')],
            [InlineKeyboardButton(text='Список слов 📋', callback_data='key_word_list')],
            [InlineKeyboardButton(text='◀️ Назад', callback_data='menu')]
        ])
        await message.answer('🔑 Меню ключевых слов, которые будут искаться в сообщениях.', reply_markup=markup)


@router.callback_query(filters.Text('key_word_list'))
async def key_word_list(callback: types.CallbackQuery):
     msg = '🔑 Список ключевых слов:\n\n'

     for index, key_word in enumerate(config.key_words):
        msg += f'{index+1}. {key_word}\n'
     
     if (not len(config.key_words)):
        msg += 'Список пуст.'

     await callback.message.answer(msg)


@router.callback_query(filters.Text('delete_key_word'))
async def delete_key_word(callback: types.CallbackQuery, state: FSMContext):
    msg = '🗑 Укажите номер слова, которое нужно удалить (можно несколько, через запятую)\n\n'

    for index, key_word in enumerate(config.key_words):
        msg += f'{index+1}. {key_word}\n'
     
    if (not len(config.key_words)):
        await callback.message.answer('Нет слов для удаления.')
        return
    markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='❌ Отмена')]], resize_keyboard=True)
    await callback.message.answer(msg, reply_markup=markup)
    await state.set_state(KeyWordsState.delete)


@router.message(KeyWordsState.delete)
async def delete(message: types.Message, state: FSMContext):
    try:
        msg = '✅ Успешно удалено'
        values = message.text.split('\n')
        for value in values:
            if value.strip() == '❌ Отмена':
                msg = 'Возвращаемся назад.'
                break
            if value.strip().lower() not in config.key_words:
                await message.answer(f'Ключевое слово <b>{value.strip()}</b> отсутствует', parse_mode='html')
                continue
            config.key_words.remove(value)
            db.delete('key_words', 'word', value)
        await message.answer(msg, reply_markup=ReplyKeyboardRemove())
    except:
        await message.answer('❌ Ошибка при удалении', reply_markup=ReplyKeyboardRemove())
        print(format_exc())
    finally:
        await state.clear()
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Добавить слово 📥', callback_data='add_key_word'), InlineKeyboardButton(text='Удалить слово 🗑', callback_data='delete_key_word')],
            [InlineKeyboardButton(text='Список слов 📋', callback_data='key_word_list')],
            [InlineKeyboardButton(text='◀️ Назад', callback_data='menu')]
        ])
        await message.answer('🔑 Меню ключевых слов, которые будут искаться в сообщениях.', reply_markup=markup)
