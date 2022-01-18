from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide2.QtCore import QUrl
import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import requests
from db.database import ItchificationDB
from config.config import TWITCH_CLIENT_ID
from deepdiff import DeepDiff


class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        dbconn = ItchificationDB()
        url = info.requestUrl().toString()

        if url.__contains__('#access_token'):
            o = urlparse(url)
            token_start = o.fragment.index('=')
            token_end = o.fragment.index('&')
            token = o.fragment[token_start+1:token_end]
            dbconn.insert_token(token)


class Twitch:

    def __init__(self):
        load_dotenv()
        self.browser = QWebEngineView()
        self.dbconn = ItchificationDB()
        self.twitch_client_id = TWITCH_CLIENT_ID
        self.user_id = ""
        # TODO get twitch_token from DB
        self.twitch_token = os.getenv('T_TOKEN')
        self._followed = []
        self.get_followed()
        self._live = []

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
        self.user_id = self.__api_request('users').json()['data'][0]['id']
        followed = self.__api_request(
            "users/follows?from_id=" + self.user_id + "&first=100")
        
        followed_list_ids = [f['to_id'] for f in followed.json()['data']]
        self.populate_followed_info(followed_list_ids)

    def populate_followed_info(self, followed_list):
        query_string = "&id=".join(followed_list)
        self._followed = self.__api_request(
            "users?id=" + query_string).json()["data"]

        self.dbconn.insert_followed(self._followed)

    def get_live_streams(self):
        live_streams = self.__api_request("streams/followed?user_id=" + self.user_id).json()["data"]
        # print(live_streams)
        live = False
        for i in self._followed:
            for j in live_streams:
                if i["id"] == j["user_id"]:
                    live = True
                    # change ui to indicate live streamer
                    # if live stream has been added, use a desktop notifcation
                    print('fuckinghell it works!!')
        import dbus
        if live:
            item = "org.freedesktop.Notifications"

            notify_intf = dbus.Interface(
                dbus.SessionBus().get_object(item, "/"+item.replace(".", "/")), item)

            notify_intf.Notify(
                "", 0, "", "Twitch Streamer Is Live!!", "This is the notification body.",
                [], {"urgency": 1}, 10000)

    @property
    def followed(self):
        return self._followed

    # auth = TwitchAuthRequest()
    # auth.authenticate()
