from aiogram import Router, types, filters
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, Command

router = Router()


@router.message(CommandStart())
async def start(message: types.Message):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Настройки ⚙️', callback_data='settings')],
        [InlineKeyboardButton(text='Ключ-слова 🔑', callback_data='key_words'), InlineKeyboardButton(text='Стоп-слова 🛑', callback_data='stop_words')],
        [InlineKeyboardButton(text='Мониторинг чаты 🗂️', callback_data='monitoring_chats'), InlineKeyboardButton(text='Черный список 🚷', callback_data='black_list')]
    ])
    await message.answer('👋 Привет! Я - бот, который умеет пересылать сообщения из чатов по ключевым словам.', reply_markup=markup)


@router.callback_query(filters.Text('menu'))
async def menu(callback: types.CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Настройки ⚙️', callback_data='settings')],
        [InlineKeyboardButton(text='Ключ-слова 🔑', callback_data='key_words'), InlineKeyboardButton(text='Стоп-слова 🛑', callback_data='stop_words')],
        [InlineKeyboardButton(text='Мониторинг чаты 🗂️', callback_data='monitoring_chats'), InlineKeyboardButton(text='Черный список 🚷', callback_data='black_list')]
    ])
    await callback.message.answer('👋 Привет! Я - бот, который умеет пересылать сообщения из чатов по ключевым словам.', reply_markup=markup)
