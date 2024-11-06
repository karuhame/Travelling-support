from authlib.integrations.starlette_client import OAuth
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.environ.get('client_id')
CLIENT_SECRET = os.environ.get('client_secret')

# this file is for google authentication

# print(CLIENT_ID, CLIENT_SECRET)


ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

if ENVIRONMENT == 'development':
    REDIRECT_URI = 'http://localhost:8000/authenGoogle/auth'
    BASE_URL = 'http://localhost:8000'
else:
    REDIRECT_URI = 'https://pbl6-travel-fastapi-azfpceg2czdybuh3.eastasia-01.azurewebsites.net/authenGoogle/auth'
    BASE_URL = 'https://pbl6-travel-fastapi-azfpceg2czdybuh3.eastasia-01.azurewebsites.net'

# Cấu hình OAuth
oauth = OAuth()
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    client_kwargs={
        'scope': 'email openid profile',
        'redirect_url': REDIRECT_URI
    }
)
