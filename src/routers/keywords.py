from traceback import format_exc

from aiogram import Router, types, filters
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
    await callback.message.edit_text('🔑 Меню ключевых слов, которые будут искаться в сообщениях.')
    await callback.message.edit_reply_markup(callback.inline_message_id, markup)


@router.callback_query(filters.Text('add_key_word'))
async def add_key_word(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer('🔑 Укажите ключевое слово (можно несколько через запятую)')
    await state.set_state(KeyWordsState.user_input)


@router.message(KeyWordsState.user_input)
async def user_input(message: types.Message, state: FSMContext):
    try:
        for key_word in message.text.lower().split(','):
                config.key_words.append(key_word.strip())
                db.create('key_words', key_word.strip())
        await message.answer('✅ Успешно добавлено')
    except:
        await message.answer('❌ Ошибка при добавлении')
        print(format_exc())
    finally:
        await state.clear()


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

     await callback.message.answer(msg)
     await state.set_state(KeyWordsState.delete)


@router.message(KeyWordsState.delete)
async def delete(message: types.Message, state: FSMContext):
    try:
        values = [config.key_words[int(index)-1] for index in message.text.split(',')]
        for value in values:
            config.key_words.remove(value)
            db.delete('key_words', 'word', value)
        await message.answer('✅ Успешно удалено')
    except:
        await message.answer('❌ Ошибка при удалении')
        print(format_exc())
    finally:
        await state.clear()
