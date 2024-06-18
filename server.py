import os
import json
from flask import Flask, request, render_template
from plaid.api import plaid_api
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid import Configuration, ApiClient
from plaid.model.products import Products

app = Flask(__name__)

from configparser import ConfigParser

config = ConfigParser()
config.read('config.ini')
# Telegram bot token and Plaid API keys (replace with your own)
TELEGRAM_TOKEN = config['data']['TELEGRAM_TOKEN']
PLAID_CLIENT_ID = config['data']['PLAID_CLIENT_ID']
PLAID_SECRET = config['data']['PLAID_SECRET']
PLAID_ENV = 'sandbox'  # Change to 'development' or 'production' as needed

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

@app.route('/')
def index():
    try:
        request = LinkTokenCreateRequest(
            products=[Products('auth'), Products('transactions')],
            client_name="Plaid Test App",
            country_codes=[CountryCode('US')],
            language='en',
            user=LinkTokenCreateRequestUser(client_user_id="unique_user_id")
        )
        response = client.link_token_create(request)
        link_token = response['link_token']
        return render_template(template_name_or_list='index.html', link_token=link_token)
    except Exception as e:
        return str(e)


@app.route('/get_public_token', methods=['POST'])
def get_public_token():
    public_token = request.json.get('public_token')
    return {'public_token': public_token}

if __name__ == '__main__':
    app.run(port=5000)
