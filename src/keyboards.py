from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

MENU = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='Настройки ⚙️', callback_data='settings')],
    [InlineKeyboardButton(text='Ключ-слова 🔑', callback_data='key_words'), InlineKeyboardButton(text='Стоп-слова 🛑', callback_data='stop_words')],
    [InlineKeyboardButton(text='Мониторинг чаты 🗂️', callback_data='monitoring_chats'), InlineKeyboardButton(text='Черный список 🚷', callback_data='black_list')]
])

SETTINGS = InlineKeyboardMarkup([
    [InlineKeyboardButton(text='Добавить чат 📥', callback_data='add_monitoring_chats'), InlineKeyboardButton(text='Удалить чат 🗑', callback_data='delete_monitoring_chats')],
    [InlineKeyboardButton(text='Список чатов 📋', callback_data='monitoring_chats_list')],
    [InlineKeyboardButton(text='◀️ Назад', callback_data='menu')]
])
