from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
# Telegram bot token and Plaid API keys (replace with your own)
TELEGRAM_TOKEN = config['data']['TELEGRAM_TOKEN']
PLAID_CLIENT_ID = config['data']['PLAID_CLIENT_ID']
PLAID_SECRET = config['data']['PLAID_SECRET']
PLAID_ENV = 'sandbox'  # Change to 'development' or 'production' as needed

import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid import Configuration, ApiClient
 # Change to 'development' or 'production' as needed

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Plaid configuration
configuration = Configuration(
    host="https://sandbox.plaid.com",
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
    }
)
api_client = ApiClient(configuration)
client = plaid_api.PlaidApi(api_client)

# Initialize bot and dispatcher
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Command handlers
@dp.message(Command('start'))
async def send_welcome(message: Message):
    await message.answer(f'Привет, {message.from_user.first_name}! Я могу помочь тебе подключиться к Plaid API.')

@dp.message(Command('create_link_token'))
async def create_link_token(message: Message):
    try:
        request = LinkTokenCreateRequest(
            products=[Products('auth'), Products('transactions')],
            client_name="Plaid Test App",
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(client_user_id="unique_user_id")
        )
        response = client.link_token_create(request)
        await message.answer(f"Вот твой link_token: {response['link_token']}")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")

@dp.message(Command('exchange_public_token'))
async def exchange_public_token(message: Message):
    public_token = message.get_args()
    if not public_token:
        await message.answer("Пожалуйста, предоставьте public_token.")
        return
    try:
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(request)
        await message.answer(f"access_token: {response['access_token']}\nitem_id: {response['item_id']}")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
