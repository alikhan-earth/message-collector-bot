from traceback import format_exc

from aiogram import Router, types, filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
    await callback.message.edit_text('🔴 Меню стов-слов, которые будут искаться в сообщениях.')
    await callback.message.edit_reply_markup(callback.inline_message_id, markup)


@router.callback_query(filters.Text('add_stop_word'))
async def add_stop_word(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('🔴 Укажите стоп-слово (можно несколько через запятую)')
    await state.set_state(StopWordsState.user_input)


@router.message(StopWordsState.user_input)
async def user_input(message: types.Message, state: FSMContext):
    try:
        for stop_word in message.text.lower().split(','):
                config.stop_words.append(stop_word.strip())
                db.create('stop_words', stop_word.strip())
        await message.answer('✅ Успешно добавлено')
    except:
        await message.answer('❌ Ошибка при добавлении')
        print(format_exc())
    finally:
        await state.clear()


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

    await callback.message.answer(msg)
    await state.set_state(StopWordsState.delete)


@router.message(StopWordsState.delete)
async def delete(message: types.Message, state: FSMContext):
    try:
        values = [config.stop_words[int(index)-1] for index in message.text.split(',')]
        for value in values:
            config.stop_words.remove(value)
            db.delete('stop_words', 'word', value)
        await message.answer('✅ Успешно удалено')
    except:
        await message.answer('❌ Ошибка при удалении')
        print(format_exc())
    finally:
        await state.clear()
