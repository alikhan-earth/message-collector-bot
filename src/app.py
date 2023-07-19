import nest_asyncio
nest_asyncio.apply()

import os
import asyncio
from pprint import pprint
from random import randint
from traceback import format_exc

from telethon import TelegramClient, events
from telethon import functions
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors.rpcerrorlist import UsernameInvalidError, ChannelPrivateError
from telethon.errors.rpcerrorlist import InviteRequestSentError
from telethon.errors.rpcerrorlist import InviteHashExpiredError

import config
from bot import dp, bot
from db import db

API_ID = os.environ['API_ID']
API_HASH = os.environ['API_HASH']
chats = []
private_channels_ids = {}

client = TelegramClient('session_name', API_ID, API_HASH, system_version="4.16.30-vxALIKHANEEE")
client.start()

os.system('touch log.txt')

def printp(*values):
    with open('log.txt', 'a') as file:
        for value in values:
            file.write(str(value) + '\n')
    print(*values)


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
    await asyncio.sleep(randint(60, 300))
    printp(event.chat.to_dict()['username'], private_channels_ids, config.monitoring_chats)
    printp(1, event.chat.to_dict()['username'] not in config.monitoring_chats, event.chat.to_dict()['id'] not in private_channels_ids.values())
    if not event.chat: return

    if not config.bot_enabled:
        return
    
    if event.chat.to_dict()['username'] not in config.monitoring_chats and event.chat.to_dict()['id'] not in private_channels_ids.values():
        return
    
    is_group = event.chat.to_dict()['gigagroup'] or event.chat.to_dict()['megagroup']

    if not event.message.to_dict()['from_id']:
        user_info = {'username': None}
    else:
        user_info = {'username': (await event.get_sender()).username}
    printp(2, is_group, user_info)
    if is_group and user_info:
        if user_info['username'] in config.black_list:
            return
    printp(1, config.stop_words, config.key_words, event.message.text.lower())
    for word in config.stop_words:
        if word in event.message.text.lower():
            return
    for word in config.key_words:
        if word.lower() in event.message.text.lower():
            break
    else:
        if len(config.key_words):
            return
    printp(2, 3)
    message = event.message.text.lower().strip()
    printp(message, config.messages, config.duplicate_filter)
    if message in config.messages and config.duplicate_filter:
        return
    printp(3)

    config.messages.append(message)
    printp(user_info)
    if config.send_mode == 'forwarding':
        user_link = """**[@{0}](http://t.me/{1})**"""
        link = """**[{0}]({1})**"""
        message_link = None
        chat = f"@{event.chat.to_dict()['username']}" if event.chat.to_dict()['username'] else list(private_channels_ids.keys())[list(map(str, private_channels_ids.values())).index(str(event.chat.to_dict()['id']))]

        if not is_group and ('joinchat' in chat or '+' in chat):
            message_link = f"https://t.me/c/{event.chat.to_dict()['id']}/{event.message.to_dict()['id']}"
        elif not ('joinchat' in chat or '+' in chat):
            message_link = f"https://t.me/{event.chat.to_dict()['username']}/{event.message.to_dict()['id']}"
        elif is_group and ('joinchat' in chat or '+' in chat):
            message_link = list(private_channels_ids.keys())[list(map(str, private_channels_ids.values())).index(str(event.chat.to_dict()['id']))]

        message += f"""\n\n👤 {'`Отсутствует`' if not user_info['username'] else user_link.format(user_info['username'], user_info['username'])}\n💬 {link.format(chat, message_link)}"""
    printp(4, config.chats)
    for chat in config.chats:
        printp(chat, private_channels_ids)
        if 'joinchat' in chat or '+' in chat:
            printp('\nyeah\n')
            try:
                await bot.send_message('-100' + private_channels_ids[chat], message, parse_mode='markdown', disable_web_page_preview=True)
            except:
                entity = await client.get_entity(chat)
                await client.send_message(entity = entity,message=message, parse_mode='markdown', link_preview=False)
        else:
            printp('\nno\n')
            chat_id = (await get_chat_info(chat))

            if chat_id['gigagroup'] or chat_id['megagroup']:
                await bot.send_message('-100' + str(chat_id['id']), message, parse_mode='markdown', disable_web_page_preview=True)
            else:
                entity = await client.get_entity(chat)
                await client.send_message(entity = entity,message=message, parse_mode='markdown', link_preview=False)
        await asyncio.sleep(randint(60, 240))

async def check_chats():
    try:
        global chats
        while True:
            chat_set = set(config.monitoring_chats) - set(chats)

            if len(chat_set):
                printp(chat_set)
                for chat in chat_set:
                    try:
                        printp(chat)
                        await client(JoinChannelRequest(chat))
                        if '+' in chat or 'joinchat' in chat:
                            chat_id = (await get_chat_info(chat))['id']
                            private_channels_ids[chat] = chat_id
                        printp('+')
                    except InviteRequestSentError:
                        continue
                    except (InviteHashExpiredError, ValueError):
                        printp('-')
                        config.monitoring_chats.remove(chat)
                        db.delete('monitoring_chats', 'chat_id', chat)
                        continue
                    except ChannelPrivateError:
                        result = await client(ImportChatInviteRequest(chat[chat.index('/'):].replace('/', '').replace('+', '')))
                        result_dict = result.to_dict()
                        printp('result_dict', result_dict)
                        if len(result_dict['chats']):
                            private_channels_ids[chat] = result_dict['chats'][0]['id']
                chats = config.monitoring_chats[:]
            
            to_delete = []

            for key in private_channels_ids.keys():
                if key not in config.monitoring_chats:
                    to_delete.append(key)

            for key in to_delete:
                del private_channels_ids[key]
            await asyncio.sleep(5)
    except:
        with open(f'{randint(1, 100000)}.txt', 'w') as file:
            file.write(format_exc())


async def start_handle():
    try:
        await client.run_until_disconnected()
    except:
        with open(f'{randint(1, 100000)}.txt', 'w') as file:
            file.write(format_exc())


async def start_bot():
    try:
        await dp.start_polling(bot, skip_updates=True)
    except:
        with open(f'{randint(1, 100000)}.txt', 'w') as file:
            file.write(format_exc())


async def main():
    f1 = loop.create_task(start_bot())
    f2 = loop.create_task(start_handle())
    f3 = loop.create_task(check_chats())
    await asyncio.ensure_future(f3)
    await asyncio.wait([f1, f2])


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
