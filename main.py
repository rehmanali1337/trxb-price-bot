from telethon import TelegramClient, events, types
import json
import logging
import asyncio
import os
from exts import store
import re
from exts.db import WhiteListDB
from exts import event_handlers as eh


db = WhiteListDB()

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.ERROR)

config = json.load(open('config.json'))

PHONE_NUMBER = config.get("TELEGRAM_PHONE_NUMBER")
BOT_TOKEN = config.get("TELEGRAM_BOT_TOKEN")
ADMIN_USERNAME = config.get("ADMIN_USERNAME")
if not os.path.exists('sessionFiles'):
    os.mkdir('sessionFiles')

PROXY = config.get("PROXY")
if PROXY:
    import socks
    proxy_list = PROXY.split(':')
    proxy = {
        'proxy_type': socks.PROXY_TYPE_SOCKS5,
        'addr': proxy_list[0],
        'port': int(proxy_list[1]),
        'username': proxy_list[2],
        'password': proxy_list[3]
    }
    bot = TelegramClient('sessionFiles/bot',
                         config.get("TELEGRAM_API_ID"), config.get("TELEGRAM_API_HASH"), proxy=proxy)
else:
    bot = TelegramClient('sessionFiles/bot',
                         config.get("TELEGRAM_API_ID"), config.get("TELEGRAM_API_HASH"))


def is_admin(event):
    if isinstance(event.message.peer_id, types.PeerChannel):
        return event.message.from_id.user_id == store.ADMIN.id
    elif isinstance(event.message.peer_id, types.PeerUser):
        return event.message.peer_id.user_id == store.ADMIN.id


@bot.on(events.NewMessage(pattern='/turn_on', func=is_admin))
async def newMessage(event):
    store.BOT_ON = True
    await event.respond('The bot has been turned on..')
    raise events.StopPropagation


@bot.on(events.NewMessage(pattern='/turn_off', func=is_admin))
async def newMessage(event):
    store.BOT_ON = False
    await event.respond('The bot has been turned off..')
    raise events.StopPropagation


async def prepare_store():
    store.ADMIN = await bot.get_entity(ADMIN_USERNAME)


async def setup_event_handlers():
    bot.add_event_handler(eh.remove_from_whitelist, events.NewMessage(
        pattern='/remove_whitelist ', func=is_admin))
    bot.add_event_handler(eh.whitelist_user, events.NewMessage(
        pattern='/whitelist', func=is_admin))
    bot.add_event_handler(eh.eth_price, events.NewMessage(
        pattern='/eth'))
    bot.add_event_handler(eh.btc_price, events.NewMessage(
        pattern='/btc'))
    bot.add_event_handler(eh.help_command, events.NewMessage(
        pattern='/bot'))
    bot.add_event_handler(eh.socials, events.NewMessage(
        pattern='/socials'))
    bot.add_event_handler(eh.wen_moon, events.NewMessage(
        pattern='/wen_moon'))
    bot.add_event_handler(eh.price, events.NewMessage(
        pattern='/price'))
    bot.add_event_handler(eh.newMessage, events.NewMessage)


async def on_ready():
    wait_time = 0.5
    if not bot.is_connected() or await bot.is_user_authorized():
        await asyncio.sleep(wait_time)
    await prepare_store()
    await setup_event_handlers()
    print('Bot is ready!')

try:
    bot.start(bot_token=BOT_TOKEN)
    bot.loop.create_task(on_ready())
    bot.run_until_disconnected()
except KeyboardInterrupt:
    print('Quiting bot ...')
    exit()
