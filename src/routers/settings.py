from aiogram import Router, types, filters
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.state import State, StatesGroup

import config

router = Router()


def _get_settings_text():
    format_txt = """<a href="{0}">{1}</a>"""
    return f"""⚙️ Перешли к главным настройкам бота, выберите опцию:\n\nСтатус бота: {'🟢 Онлайн' if config.bot_enabled else '🔴 Выключен'}\nФильтр дубликатов: {'🟢 Включен' if config.duplicate_filter else '🔴 Выключен'}\n\nЧаты для переотправки: {', '.join(map(lambda chat: format_txt.format('http://t.me/' + chat if 'joinchat' and chat[chat.rindex('/')+1] != '+' not in chat else chat, chat), config.chats)) if len(config.chats) else 'Список пуст'}\nРежим отправки: {'Пересылка с ссылкой' if config.send_mode == 'forwarding' else 'Копирование'}"""


def _get_settings_kb():
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Отключить бота 🤖' if config.bot_enabled else 'Включить бота 🤖', callback_data='bot')],
        [InlineKeyboardButton(text='Отключить дубликаты 🔁' if config.duplicate_filter else 'Включить дубликаты ▶️', callback_data='duplicates')],
        [InlineKeyboardButton(text='Настроить чаты 📩', callback_data='chats_settings')],
        [InlineKeyboardButton(text='◀️ Назад', callback_data='menu')]
    ])
    return markup


def _get_chats_settings_kb():
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=('✅' if config.send_mode=='copy' else '') + 'Копирование', callback_data='copy'), InlineKeyboardButton(text=('✅' if config.send_mode=='forwarding' else '') + 'Пересылка', callback_data='forwarding')],
        [InlineKeyboardButton(text='Указать чаты 📩', callback_data='chats')],
        [InlineKeyboardButton(text='◀️ К настройкам', callback_data='settings')]
    ])
    return markup


@router.callback_query(filters.Text('settings'))
async def settings(callback: types.CallbackQuery):
    message = _get_settings_text()
    markup = _get_settings_kb()

    await callback.message.answer(message, parse_mode='html', reply_markup=markup, disable_web_page_preview=True)


@router.callback_query(filters.Text('duplicates'))
async def duplicates(callback: types.CallbackQuery):
    config.duplicate_filter = not config.duplicate_filter
    message = _get_settings_text()
    markup = _get_settings_kb()

    await callback.message.answer(message, parse_mode='html', reply_markup=markup, disable_web_page_preview=True)


@router.callback_query(filters.Text('bot'))
async def bot(callback: types.CallbackQuery):
    config.bot_enabled = not config.bot_enabled
    message = _get_settings_text()
    markup = _get_settings_kb()

    await callback.message.answer(message, parse_mode='html', reply_markup=markup, disable_web_page_preview=True)


@router.callback_query(filters.Text('chats_settings'))
async def chats_settings(callback: types.CallbackQuery):
    await callback.message.answer(_get_settings_text(), parse_mode='html', reply_markup=_get_chats_settings_kb(), disable_web_page_preview=True)


@router.callback_query(filters.Text('copy'))
async def chats_settings(callback: types.CallbackQuery):
    config.send_mode = 'copy'
    await callback.message.answer(_get_settings_text(), parse_mode='html', reply_markup=_get_chats_settings_kb(), disable_web_page_preview=True)


@router.callback_query(filters.Text('forwarding'))
async def chats_settings(callback: types.CallbackQuery):
    config.send_mode = 'forwarding'
    await callback.message.answer(_get_settings_text(), parse_mode='html', reply_markup=_get_chats_settings_kb(), disable_web_page_preview=True)
