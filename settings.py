import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def auth_token():
    return os.getenv('AUTH_TOKEN')


DATABASE_URL = os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://')

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

if __name__ == '__main__':
    pass
