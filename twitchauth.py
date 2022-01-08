from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PySide2.QtCore import QUrl

from urllib.parse import urlparse


class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        url = info.requestUrl().toString()

        if url.__contains__('#access_token'):
            o = urlparse(url)
            print('fragment', o.fragment)
            start = o.fragment.index('=')
            end = o.fragment.index('&')
            substring = o.fragment[start+1:end]
            print('token is...', substring)
            print(url)


class TwitchAuthRequest:

    def __init__(self):
        self.browser = QWebEngineView()

    def authenticate(self):
        self.browser.load(QUrl("https://id.twitch.tv/oauth2/authorize?client_id=4dcpxwjtz5n2h0323mrutraf8k8gkc"
                               "&redirect_uri=http://localhost&response_type=token+id_token&scope=openid "
                               "user:read:follows"))
        self.browser.show()

