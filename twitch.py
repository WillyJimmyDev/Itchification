from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide2.QtCore import QUrl
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import requests
from db.database import ItchificationDB


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
        self.dbconn = ItchificationDB()
        self._followed = []
        self.get_followed()

    def authenticate(self):
        self.browser.load(QUrl("https://id.twitch.tv/oauth2/authorize?client_id=" + self.twitch_client_id +
                               "&redirect_uri=http://localhost&response_type=token+id_token&scope=openid "
                               "user:read:follows"))
        self.browser.show()

    def __api_request(self, endpoint):
        url = "https://api.twitch.tv/helix/" + endpoint
        headers = {"Client-ID": self.twitch_client_id,
                   "Authorization": "Bearer " + self.twitch_token}
        return requests.get(url, headers=headers)

    def get_followed(self):
        followed_list = []
        userid = self.__api_request('users').json()['data'][0]['id']
        followed = self.__api_request("users/follows?from_id=" + userid + "&first=100")
        for f in followed.json()['data']:
            followed_list.append(f['to_id'])

        self.populate_followed_info(followed_list)

    def populate_followed_info(self, followed_list):
        query_string = "&id=".join(followed_list)
        self._followed = self.__api_request("users?" + query_string).json()["data"]
        print(self._followed)
        self.dbconn.insert_followed(self._followed)

    @property
    def followed(self):
        return self._followed

    # auth = TwitchAuthRequest()
    # auth.authenticate()
