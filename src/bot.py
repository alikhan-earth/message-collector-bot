import os
import asyncio

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage

from db import db
import config

storage = MemoryStorage()
bot = Bot(token=os.environ['BOT_TOKEN'])
dp = Dispatcher(storage=storage)

[config.key_words.append(row[0]) for row in db.get_all('key_words')]
[config.stop_words.append(row[0]) for row in db.get_all('stop_words')]
[config.black_list.append(row[0]) for row in db.get_all('black_list')]
[config.chats.append(row[0]) for row in db.get_all('chats')]
[config.monitoring_chats.append(row[0]) for row in db.get_all('monitoring_chats')]

from routers import (
    chatsr,
    keywords, 
    start, 
    settings, 
    blacklist, 
    stopwords,
    monitoringchats
)

dp.include_routers(settings.router, start.router, keywords.router, blacklist.router, stopwords.router, monitoringchats.router, chatsr.router)
