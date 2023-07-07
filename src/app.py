import nest_asyncio
nest_asyncio.apply()

import os
import asyncio
import threading
import json
from pprint import pprint

from telethon import TelegramClient, events
from telethon import functions

import config
from bot import *

API_ID = os.environ['API_ID']
API_HASH = os.environ['API_HASH']

client = TelegramClient('session_name', API_ID, API_HASH)
client.start()


async def get_full_user_info(event):
    full_user_info = await client(functions.users.GetFullUserRequest(id=event.message.to_dict()['from_id']['user_id']))
    return full_user_info.to_dict()['users'][0]


async def get_chat_info(username):
    chat_info = await client(functions.channels.GetFullChannelRequest(username))
    return chat_info.to_dict()['chats'][0]


@client.on(events.NewMessage())
async def handler(event):
    if not config.bot_enabled:
        return
    
    if not event.chat: return

    if event.chat.to_dict()['username'] not in config.monitoring_chats:
        return

    user_info = await get_full_user_info(event)

    if user_info['username'] in config.black_list:
        return

    for word in config.stop_words:
        if word in event.message.text.lower():
            return

    for word in config.key_words:
        if word not in event.message.text.lower():
            return

    message = event.message.text.lower().strip()

    if message in config.messages and config.duplicate_filter:
        return

    config.messages.append(message)

    if config.send_mode == 'forwarding':
        message += f"""\n\n<b>Пользователь</b>: <a href="http://t.me/{user_info['username']}">{user_info['username']}</a>\n<b>Чат</b>: <a href="http://t.me/{event.chat.to_dict()['username']}">{event.chat.to_dict()['title']}</a>"""

    for chat in config.chats:
        chat_id = (await get_chat_info(chat))['id']
        await bot.send_message('-100' + str(chat_id), message, parse_mode='html', disable_web_page_preview=True)


async def start_handle():
    await client.run_until_disconnected()


async def start_bot():
    await dp.start_polling(bot, skip_updates=True)


async def main():
    f1 = loop.create_task(start_bot())
    f2 = loop.create_task(start_handle())
    await asyncio.run(f1)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
