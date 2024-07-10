import asyncio
from telethon import TelegramClient
import configparser
config = configparser.ConfigParser()
config.read('config.ini')

api_id = config.get('Settings', 'api_id')
api_hash = config.get('Telegram', 'api_hash')

async def auth():
    if not hasattr(auth, 'client'):
        client = TelegramClient('main_session', api_id, api_hash)
        await client.start()
        setattr(auth, 'client', client)
    return auth.client

async def send_message(client, bot_username, message):
    bot = await client.get_entity(bot_username)
    await client.send_message(bot, message)

async def get_response(client, bot_username):
    bot = await client.get_entity(bot_username)
    messages = await client.get_messages(bot, limit=1)
    if messages:
        return messages[0]
    return None

async def click_first_button(message):
    if message.buttons:
        await message.click(1)  
        return True
    return False


