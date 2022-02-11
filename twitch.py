from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide2.QtCore import QUrl, Signal, QObject, Slot,QTimer
from PySide2.QtWidgets import QMessageBox
from urllib.parse import urlparse
import requests
from db.database import ItchificationDB
from config.config import TWITCH_CLIENT_ID
import dbus
from deepdiff import DeepDiff


class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        twitch = Twitch()
        url = info.requestUrl().toString()

        if url.__contains__('#access_token'):
            o = urlparse(url)
            token_start = o.fragment.index('=')
            token_end = o.fragment.index('&')
            token = o.fragment[token_start+1:token_end]
            twitch.save_token(token)
            # need to close browser after saving token and refresh main 



class Twitch(QObject):
    siggy = Signal(object)

    def __init__(self):
        super().__init__()
        self.browser = QWebEngineView()
        self.dbconn = ItchificationDB()
        self.twitch_client_id = TWITCH_CLIENT_ID
        self.user_id = ""
        self.twitch_token = self.dbconn.get_token()
        if not self.twitch_token:
            self.authenticate()
        self._followed = []
        self._live = []
        # self.siggy.connect(self._my_slot)

    # load a web view for Twitch auth flow.
    # The WebEngineUrlRequestInterceptor reads the token from the auth flow and inserts it in the db
    def authenticate(self):
        self.browser.load(
            QUrl(
                (
                    f'https://id.twitch.tv/oauth2/authorize?client_id={self.twitch_client_id}'
                    + "&redirect_uri=http://localhost&response_type=token+id_token&scope=openid "
                    "user:read:follows"
                )
            )
        )

        self.browser.show()

    def check_auth(self):
        if not self.twitch_token: 
            return False
        url = "https://id.twitch.tv/oauth2/validate"
        headers = {"Authorization": f'Bearer {self.twitch_token}'}
        r = requests.get(url, headers=headers)
        return r.status_code == 200

    def __api_request(self, endpoint):
        url = f'https://api.twitch.tv/helix/{endpoint}'
        headers = {
            "Client-ID": self.twitch_client_id,
            "Authorization": f'Bearer {self.twitch_token}',
        }

        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return r
        return False

    def save_token(self,token):
        self.twitch_token = token
        self.dbconn.insert_token(token)
        self._notify_authenticated()

    def get_followed(self):
        print('called get_followed')
        request = self.__api_request('users')
        self.user_id = request.json()['data'][0]['id']
        followed = self.__api_request(
            f'users/follows?from_id={self.user_id}&first=100'
        )

        followed_list_ids = [f['to_id'] for f in followed.json()['data']]
        self.populate_followed_info(followed_list_ids)

    def populate_followed_info(self, followed_list):
        query_string = "&id=".join(followed_list)
        self._followed = self.__api_request(f'users?id={query_string}').json()["data"]

        self.dbconn.insert_followed(self._followed)
        # hold a temporary value for live status initailly set to 0
        for i in self.followed:
            i["live"] = 0

        self._get_live_streams()
        if self._live:
            for l in self._live:
                for f in self._followed:
                    if f["id"] == l["user_id"]:
                        f["live"] = 1
                        f['description'] = l['title']


    def _get_live_streams(self):
        live_streams = self.__api_request(
            f'streams/followed?user_id={self.user_id}'
        ).json()["data"]


        if not live_streams:
            self._live.clear()
            return
        if not self._live: # all live streamers are new
            print('first run loading live streams')
            self._live = live_streams
            self.siggy.emit(['1','2','3']) # doesn't get called on first run why?
            for i in self._live:
                self._notify_live(i["user_name"],i["title"])
            return
        # else:
        #     self._live.sort(key=lambda x: x['user_id'], reverse=False)
        #     live_streams.sort(key=lambda x: x['user_id'], reverse=False)
        #     # print(self._live)
        #     # print(live_streams)
        #     # ddiff = DeepDiff(self._live, live_streams, exclude_paths={"root['ingredients']"})
        #     # print(ddiff)
        #     print(self._live == live_streams)
        #     if self._live == live_streams: # nothing has changed, move on
        #         return
        for i in live_streams:
            if i not in self._live:
                self._live.append(i)
                self._notify_live(i["user_name"],i["title"])
                self.siggy.emit(['4','5','6']) # should call when new streamer goes live                          

    def _notify_live(self, username, title):
        item = "org.freedesktop.Notifications"

        notify_intf = dbus.Interface(
        dbus.SessionBus().get_object(item, "/"+item.replace(".", "/")), item)

        notify_intf.Notify(
            "",
            0,
            "",
            f'{username} Has Just Gone Live!',
            title,
            [],
            {"urgency": 1},
            10000,
        )
    
    def _notify_authenticated(self):
        item = "org.freedesktop.Notifications"

        notify_intf = dbus.Interface(
        dbus.SessionBus().get_object(item, "/"+item.replace(".", "/")), item)

        notify_intf.Notify(
        "", 0, "", "You are successfully authenticated with Twitch", "Authentication Successful",
        [], {"urgency": 1}, 10000)

    # @Slot()
    # def _my_slot(self):
    #     print('new live streamer')


    @property
    def followed(self):
        return self._followed

    @property
    def live(self):
        return self._live
