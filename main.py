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
from plaid.model.accounts_get_request import AccountsGetRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid import Configuration, ApiClient
from datetime import datetime, timedelta
FLASK_SERVER_URL = 'https://e56a-31-173-81-181.ngrok-free.app/'  # URL вашего Flask-сервера

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

# Store the access token
access_token = ''

# Command handlers
@dp.message(Command('start'))
async def send_welcome(message: Message):
    await message.answer(f'Привет, {message.from_user.first_name}! Я могу помочь тебе подключиться к Plaid API. Перейди по этой ссылке, чтобы подключить свой банковский аккаунт: {FLASK_SERVER_URL}')

@dp.message(Command('exchange_public_token'))
async def exchange_public_token(message: Message):
    global access_token
    public_token = message.text.split()[-1]
    if not public_token:
        await message.answer("Пожалуйста, предоставьте public_token.")
        return
    try:
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = client.item_public_token_exchange(request)
        access_token = response['access_token']
        await message.answer(f"access_token: {access_token}\nitem_id: {response['item_id']}")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")

@dp.message(Command('accounts'))
async def get_accounts(message: Message):
    if not access_token:
        await message.answer("Пожалуйста, сначала выполните команду /exchange_public_token.")
        return
    try:
        request = AccountsGetRequest(access_token=access_token)
        response = client.accounts_get(request)
        accounts_info = "\n".join([f"Account: {account.name}, Type: {account.type}, Subtype: {account.subtype}" for account in response['accounts']])
        await message.answer(f"Accounts:\n{accounts_info}")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")

@dp.message(Command('transactions'))
async def get_transactions(message: Message):
    if not access_token:
        await message.answer("Пожалуйста, сначала выполните команду /exchange_public_token.")
        return
    try:
        start_date = (datetime.now() - timedelta(days=30)).date()
        end_date = datetime.now().date()
        request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date,
            end_date=end_date,
            options=TransactionsGetRequestOptions(count=10)
        )
        response = client.transactions_get(request)
        transactions_info = "\n".join([f"Amount: {transaction.amount}, Name: {transaction.name}" for transaction in response['transactions']])
        await message.answer(f"Recent transactions:\n{transactions_info}")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")

@dp.message(Command('balance'))
async def get_balance(message: Message):
    if not access_token:
        await message.answer("Пожалуйста, сначала выполните команду /exchange_public_token.")
        return
    try:
        request = AccountsBalanceGetRequest(access_token=access_token)
        response = client.accounts_balance_get(request)
        balance_info = "\n".join([f"Account: {account.name}, Balance: {account.balances.available}" for account in response['accounts']])
        await message.answer(f"Account balances:\n{balance_info}")
    except Exception as e:
        await message.answer(f"Произошла ошибка: {str(e)}")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())