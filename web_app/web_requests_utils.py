import requests
from requests import auth


class BearerToken(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = f"Bearer {self.token}"
        return r

def send_get_request_with_bearer_auth(url: str, bearer_token: str, proxies:dict) -> dict:
    response = requests.get(url, auth=BearerToken(bearer_token),proxies=proxies)
    return response.json()


def send_post_request(url: str, data: dict, proxies:dict) -> dict:
    response = requests.post(url, data, proxies=proxies)
    return response.json()
