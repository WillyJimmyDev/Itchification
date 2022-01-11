from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide2.QtCore import QUrl
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import requests


class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl().toString()

        if url.__contains__('#access_token'):
            o = urlparse(url)
            # print('fragment', o.fragment)
            start = o.fragment.index('=')
            end = o.fragment.index('&')
            substring = o.fragment[start+1:end]
            # print('token is...', substring)
            # print(url)


class Twitch:

    load_dotenv()
    twitch_client_id = os.getenv('T_CLIENT_ID')
    twitch_token = os.getenv('T_TOKEN')

    def __init__(self):
        self.browser = QWebEngineView()

    def authenticate(self):
        self.browser.load(QUrl("https://id.twitch.tv/oauth2/authorize?client_id=" + self.twitch_client_id +
                               "&redirect_uri=http://localhost&response_type=token+id_token&scope=openid "
                               "user:read:follows"))
        self.browser.show()

    def api_request(self, endpoint):
        url = "https://api.twitch.tv/helix/" + endpoint
        headers = {"Client-ID": self.twitch_client_id,
                   "Authorization": "Bearer " + self.twitch_token}
        return requests.get(url, headers=headers)

    def get_followed_list(self):
        followed_list = []
        userid = self.api_request('users').json()['data'][0]['id']
        followed = self.api_request("users/follows?from_id=" + userid + "&first=100")
        for f in followed.json()['data']:
            followed_list.append(f['to_id'])

        return self.get_user_info(followed_list)

    def get_user_info(self, follows):
        if isinstance(follows, list):
            query_string = "&id=".join(follows)
            user_info = self.api_request("users?" + query_string).json()["data"]
            return user_info

    # auth = TwitchAuthRequest()
    # auth.authenticate()
