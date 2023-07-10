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
private_channels_ids = {}

client = TelegramClient('session_name', API_ID, API_HASH, system_version="4.16.30-vxALIKHANEEE")
client.start()


async def get_chat_info(username):
    chat_info = await client(functions.channels.GetFullChannelRequest(username))
    return chat_info.to_dict()['chats'][0]


@client.on(events.NewMessage())
async def handler(event):
    print(event.message.to_dict(), event.chat.to_dict())
    if not config.bot_enabled:
        return

    if not event.chat: return

    if event.chat.to_dict()['username'] not in config.monitoring_chats and event.chat.to_dict()['id'] not in private_channels_ids.values():
        return
    
    is_group = event.chat.to_dict()['gigagroup'] or event.chat.to_dict()['megagroup']
    user_info = await client.get_entity(event.message.from_id.user_id)
    print(user_info.username)
    if is_group:
        if user_info.username in config.black_list:
            return
    print(1)
    for word in config.stop_words:
        if word in event.message.text.lower():
            return
    print(event.message.text.lower())
    for word in config.key_words:
        print(word.lower())
        if word.lower() in event.message.text.lower():
            break
    else:
        if len(config.key_words):
            return
    print(2, 3)
    message = event.message.text.lower().strip()
    print(message, config.messages, config.duplicate_filter)
    if message in config.messages and config.duplicate_filter:
        return
    print(3)

    config.messages.append(message)

    if config.send_mode == 'forwarding':
        user_link = """<a href="http://t.me/{0}">{1}</a>"""
        link = """<a href="http://t.me/{0}\""""
        message += f"""\n\n<b>Пользователь</b>: {'Удалено' if not user_info.username else user_link.format(user_info.username, user_info.username)}\n<b>Чат</b>: {link.format(event.chat.to_dict()['username']) if str(event.chat.to_dict()['id']) not in map(str, private_channels_ids.values()) else private_channels_ids[private_channels_ids.keys()[list(map(str, private_channels_ids.values())).index(str(event.chat.to_dict()['id']))]]}>{event.chat.to_dict()['title']}</a>"""
    print(4, config.chats)
    for chat in config.chats:
        print(chat, private_channels_ids)
        if 'AAAAA' in chat and 'joinchat' in chat or '+' in chat:
            print('\nyeah\n')
            try:
                await bot.send_message('-100' + private_channels_ids[chat], message, parse_mode='html', disable_web_page_preview=True)
            except:
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
        await asyncio.sleep(30)
    await asyncio.sleep(40)

async def check_chats():
    global chats
    while True:
        chat_set = set(config.monitoring_chats) - set(chats)

        if len(chat_set):
            for chat in set(config.monitoring_chats) - set(chats):
                if chat in config.monitoring_chats and chat in chats:
                    continue

                try:
                    await client(JoinChannelRequest(chat))
                except (ChannelPrivateError, ValueError):
                    result = await client(ImportChatInviteRequest(chat[chat.index('A'):] if '+' not in chat else chat[chat.rindex('/')+2:]))
                    result_dict = result.to_dict()
                    print('result_dict', result_dict)
                    if len(result_dict['chats']):
                        private_channels_ids[chat] = result_dict['chats'][0]['id']
            chats = config.monitoring_chats[:]
        
        to_delete = []

        for key in private_channels_ids.keys():
            if key not in config.monitoring_chats:
                to_delete.append(key)

        for key in to_delete:
            del private_channels_ids[key]
        await asyncio.sleep(20)


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
