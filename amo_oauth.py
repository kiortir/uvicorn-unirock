import requests
from requests.structures import CaseInsensitiveDict

from .settings import CLIENT_ID, CLIENT_SECRET


def get_new_tokens(token: str, token_type: str) -> dict:
    url = "https://unirock.amocrm.ru/oauth2/access_token"

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    if token_type == 'refresh_token':
        data = '{"%s":"04bfd9ed-3fc2-4eec-8f68-48adcb24960e","%s":"79ldWvYS2IfZEK3WdINDPPEfvfQ7BjVp1RAYHKYz1olfGtZGEDCeIG8UjCubWGod","grant_type":"refresh_token","refresh_token": "%s","redirect_uri":"https://unirock.ru/"}' % (
            CLIENT_ID, CLIENT_SECRET, token)
    else:
        data = '{"%s":"04bfd9ed-3fc2-4eec-8f68-48adcb24960e","%s":"79ldWvYS2IfZEK3WdINDPPEfvfQ7BjVp1RAYHKYz1olfGtZGEDCeIG8UjCubWGod","grant_type":"authorization_code","code": "%s","redirect_uri":"https://unirock.ru/"}' % (
            CLIENT_ID, CLIENT_SECRET, token)

    response = requests.post(url, headers=headers, data=data, timeout=5)
    if response.status_code != 200:
        raise Exception('Auth issues, enter new auth token')
    tokens = response.json()
    return tokens
