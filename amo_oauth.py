import requests
from requests.structures import CaseInsensitiveDict


# def get_by_auth_token(auth_token=AUTH_TOKEN):
#     url = "https://unirock.amocrm.ru/oauth2/access_token"
#
#     headers = CaseInsensitiveDict()
#     headers["Content-Type"] = "application/json"
#
#     data = '{"client_id":"04bfd9ed-3fc2-4eec-8f68-48adcb24960e","client_secret":"79ldWvYS2IfZEK3WdINDPPEfvfQ7BjVp1RAYHKYz1olfGtZGEDCeIG8UjCubWGod","grant_type":"authorization_code","code": "%s","redirect_uri":"https://unirock.ru/"}' % (
#         auth_token)
#     response = requests.post(url, headers=headers, data=data)
#     if response.status_code != 200:
#         raise Exception(response.json()['hint'])
#     tokens = response.json()
#     expires_in = tokens['expires_in']
#     new_refresh_token = tokens['refresh_token']
#     new_access_token = tokens['access_token']
#     return tokens


def get_new_tokens(token: str, token_type: str) -> dict:
    url = "https://unirock.amocrm.ru/oauth2/access_token"

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"

    if token_type == 'refresh_token':
        data = '{"client_id":"04bfd9ed-3fc2-4eec-8f68-48adcb24960e","client_secret":"79ldWvYS2IfZEK3WdINDPPEfvfQ7BjVp1RAYHKYz1olfGtZGEDCeIG8UjCubWGod","grant_type":"refresh_token","refresh_token": "%s","redirect_uri":"https://unirock.ru/"}' % (
            token)
    else:
        data = '{"client_id":"04bfd9ed-3fc2-4eec-8f68-48adcb24960e","client_secret":"79ldWvYS2IfZEK3WdINDPPEfvfQ7BjVp1RAYHKYz1olfGtZGEDCeIG8UjCubWGod","grant_type":"authorization_code","code": "%s","redirect_uri":"https://unirock.ru/"}' % (
            token)
    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        raise Exception('Auth issues, enter new auth token')
    tokens = response.json()
    expires_in = tokens['expires_in']
    new_refresh_token = tokens['refresh_token']
    new_access_token = tokens['access_token']
    return tokens
