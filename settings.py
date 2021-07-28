import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def auth_token():
    return os.getenv('AUTH_TOKEN')


DATABASE_URL = 'postgresql://hnlwdnokggrlgm:86244c3dcf615ecb49b4adfc61ea5c51e07f1b11e9ff831c7fba6d9dff852b82@ec2-34-194-130-103.compute-1.amazonaws.com:5432/d204k3r3jcgi36'
#DATABASE_URL = os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://')
if __name__ == '__main__':
    pass
