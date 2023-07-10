import nest_asyncio
nest_asyncio.apply()

import os
import asyncio

from telethon import TelegramClient, events
from telethon import functions
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors.rpcerrorlist import UsernameInvalidError, ChannelPrivateError

import config
from bot import dp, bot

API_ID = os.environ['API_ID']
API_HASH = os.environ['API_HASH']
chats = []
private_channels_ids = []

client = TelegramClient('session_name', API_ID, API_HASH, system_version="4.16.30-vxALIKHANEEE")
client.start()


async def get_full_user_info(event):
    if event.message.to_dict()['from_id']:
        full_user_info = await client(functions.users.GetFullUserRequest(id=event.message.to_dict()['from_id']['user_id']))
        return full_user_info.to_dict()['users'][0]
    return {"username": event.chat.to_dict()['username']}


async def get_chat_info(username):
    chat_info = await client(functions.channels.GetFullChannelRequest(username))
    return chat_info.to_dict()['chats'][0]


@client.on(events.NewMessage())
async def handler(event):
    print(event.message.text, event.chat.to_dict())
    if not config.bot_enabled:
        return

    if not event.chat: return

    if event.chat.to_dict()['username'] not in config.monitoring_chats and event.chat.to_dict()['id'] not in private_channels_ids:
        return
    
    is_group = event.chat.to_dict()['gigagroup'] or event.chat.to_dict()['megagroup']
    user_info = await get_full_user_info(event)

    if is_group:
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
        print(chat, 'AAAAA' in chat and 'joinchat' in chat or chat[chat.rindex('/')+1] == '+')
        if 'AAAAA' in chat and 'joinchat' in chat or chat[chat.rindex('/')+1] == '+':
            print('\nyeah\n')
            entity = await client.get_entity(chat)
            await client.send_message(entity = entity,message=message, parse_mode='html', link_preview=False)
        else:
            print('\nno\n')
            chat_id = (await get_chat_info(chat))

            if chat_id['gigagroup'] or chat_id['megagroup']:
                await bot.send_message('-100' + str(chat_id['id']), message, parse_mode='html', disable_web_page_preview=True)
            else:
                entity = await client.get_entity(chat)
                await client.send_message(entity = entity,message=message, parse_mode='html', link_preview=False)

async def check_chats():
    global chats
    while True:
        chat_set = set(config.monitoring_chats) - set(chats)

        if len(chat_set):
            for chat in set(config.monitoring_chats) - set(chats):
                if chat in config.monitoring_chats and chat in chats:
                    continue

                try:
                    print(chat)
                    await client(JoinChannelRequest(chat))
                except (ChannelPrivateError, ValueError):
                    result = await client(ImportChatInviteRequest(chat[chat.index('A'):] if '+' not in chat else chat[chat.rindex('/')+2:]))
                    result_dict = result.to_dict()

                    if len(result_dict['chats']):
                        private_channels_ids.append(result_dict['chats'][0]['id'])
                except UsernameInvalidError:
                    config.monitoring_chats.remove(chat)
            chats = config.monitoring_chats[:]
        
        await asyncio.sleep(5)


async def start_handle():
    await client.run_until_disconnected()


async def start_bot():
    await dp.start_polling(bot, skip_updates=True)


async def main():
    f1 = loop.create_task(start_bot())
    f2 = loop.create_task(start_handle())
    f3 = loop.create_task(check_chats())
    await asyncio.ensure_future(f3)
    await asyncio.wait([f1, f2])


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
