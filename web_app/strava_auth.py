from dataclasses import dataclass, field
from typing import Union

from web_requests_utils import send_post_request


def get_authorization_link(client_id: str, redirect_url: Union[str, None] = None,
                           access_scope: Union[str, None] = None):
    return f"https://www.strava.com/oauth/authorize?client_id={client_id}" \
           f"&response_type=code" \
           f"&redirect_uri={'http://localhost/exchange_token' if not redirect_url else redirect_url}" \
           f"&scope={'read,activity:read_all' if not access_scope else access_scope}"


@dataclass
class StravaClientData:
    """
    Module to handle authorization to strava API.
    Intended usage:
        1. Initialize class with client_id and client_secret from https://www.strava.com/settings/api
        2. Get link to authorize profile in application, enter it manually in web browser
        3. Generate refresh token with obtained code from url parameter &code generate_access_token(code=&code)
        4. Generate access token based on refresh token
    """
    client_id: str
    client_secret: str
    code: Union[None, str] = None
    access_token: str = field(init=False)
    refresh_token: Union[None, str] = None
    url: str = "https://www.strava.com/oauth/token"

    def __str__(self):
        return self.__dict__

    def get_access_token(self):
        if getattr(self, 'access_token'):
            return self.access_token
        raise Exception("Access token was not generated")

    def generate_refresh_token(self, code: str):
        self.code=code
        data = {
            'client_id': f'{self.client_id}',
            'client_secret': f'{self.client_secret}',
            'code': f"{self.code}",
            'grant_type': 'authorization_code'
        }
        # TODO: Add checking for error in message
        response = send_post_request(self.url, data)
        self.refresh_token = response['refresh_token']

    def generate_access_token(self):
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
            "f": "json"
        }
        # TODO: Add checking for error in message
        response = send_post_request(self.url, data)
        self.access_token = response['access_token']
