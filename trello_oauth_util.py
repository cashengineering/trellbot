import os

from trello import util
from dotenv import load_dotenv

load_dotenv()

api_key =  os.getenv('TRELLO_API_KEY')
api_secret =  os.getenv('TRELLO_API_SECRET')

util.create_oauth_token(key=api_key, secret=api_secret)