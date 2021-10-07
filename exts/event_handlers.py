from telethon import events, TelegramClient, types, errors
from exts.db import WhiteListDB
from pycoingecko import CoinGeckoAPI
from exts import store
import re
from exts.dextools import DextoolsAPI

dex_api = DextoolsAPI()
cg = CoinGeckoAPI()
db = WhiteListDB()

links_regex = re.compile(r'((http(s)?:\/\/)?\w+\.\w+)', re.IGNORECASE)
username_regex = re.compile(r'(@\w+)', re.IGNORECASE)

all_regex = [links_regex, username_regex]


async def remove_from_whitelist(event: events.NewMessage):
    bot: TelegramClient = event._client
    username = event.message.message.replace("/remove_whitelist", "").strip()
    try:
        user = await bot.get_entity(username)
    except ValueError:
        await event.respond(f"No user found with username : {username}")
        raise events.StopPropagation
    db.remove_user(user.id)
    await event.respond(f"@{user.username} has been removed from whiltelist!")
    raise events.StopPropagation


async def whitelist_user(event: events.NewMessage):
    bot: TelegramClient = event._client
    username = event.message.message.replace("/whitelist", "").strip()
    try:
        user = await bot.get_entity(username)
    except ValueError:
        await event.respond(f"No user found with username : {username}")
        raise events.StopPropagation
    db.add_user(user.id)
    await event.respond(f"@{user.username} has been whiltelisted!")
    raise events.StopPropagation


async def eth_price(event: events.NewMessage):
    price = cg.get_price(store.ETH_ID, vs_currencies="USD")
    message = f'Current Ethereum price is: ${price[store.ETH_ID]["usd"]}'
    await event.respond(message)


async def btc_price(event: events.NewMessage):
    price = cg.get_price(store.BITCOIN_ID, vs_currencies="USD")
    message = f'Current Bitcoin price is: ${price[store.BITCOIN_ID]["usd"]}'
    await event.respond(message)


async def newMessage(event):
    # print(event.stringify())
    if not store.BOT_ON:
        return
    if isinstance(event.original_update, types.UpdateNewChannelMessage):
        user_id = event.message.from_id.user_id
    elif isinstance(event.original_update, types.UpdateNewMessage):
        user_id = event.message.peer_id.user_id
    print('Checking user in wl')
    if db.user_exists(user_id):
        print('user is whitelisted!')
        return
    for regex in all_regex:
        res = regex.findall(event.message.message)
        if len(res) != 0:
            await event.delete()
            break


async def help_command(event: events.NewMessage):
    help_message = '''
Hi, friend! I’m TREXBOT!
I’m here to help keep you updated on the TREXBITS journey and TRXB stats.
Below is a list of my commands you can use at any time:

/price I will let you know the latest TRXB Uniswap price and volume
/socials I will give you a quick reference to all of TREXBITS online platforms
/wen_moon I will tell you the expected time of TRXB to moon
/btc I will let you know the latest Bitcoin price in USD
/eth I will let you know the latest Ethereum price in USD
/bot to request this introduction
'''
    await event.respond(help_message)


async def socials(event: events.NewMessage):
    message = '''
Twitter: twitter.com/trexbits
Instagram: Instagram.com/trexbits_
Facebook: facebook.com/trexbits
Reddit: reddit.com/r/trexbits
Website: www.trexbits.com
'''
    await event.respond(message)


async def wen_moon(event: events.NewMessage):
    await event.respond("Soon Moon")


async def price(event: events.NewMessage):
    sent = await event.respond("Please wait while fetching latest price from the network ..")
    data = await dex_api.get_latest_pirce()
    message = f"USD Price : {data['result'][-1]['price']} USD"
    price_eth = '{:.18f}'.format(data["result"][-1]["priceETH"])
    message = f'{message}\nETH Price : {price_eth} ETH'
    await sent.edit(message)
