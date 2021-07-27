import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def auth_token():
    return os.getenv('AUTH_TOKEN')


DATABASE_URL = os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://')

if __name__ == '__main__':
    pass
