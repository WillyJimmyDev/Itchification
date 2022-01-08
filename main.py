import sys
import os
from dotenv import load_dotenv
from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton
from PySide2.QtCore import QSize, Qt
from twitchauth import TwitchAuthRequest, WebEngineUrlRequestInterceptor
from PySide2.QtWebEngineWidgets import QWebEngineProfile
import requests

if __name__ == '__main__':
    load_dotenv()
    twitch_client_id = os.getenv('T_CLIENT_ID')
    twitch_token = os.getenv('T_TOKEN')
    app = QApplication([])
    interceptor = WebEngineUrlRequestInterceptor()
    QWebEngineProfile.defaultProfile().setUrlRequestInterceptor(interceptor)

    # auth = TwitchAuthRequest()
    # auth.authenticate()


    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Itchification")
            button = QPushButton("Press Me!")
            self.setFixedSize(QSize(400, 300))
            self.setCentralWidget(button)

        @staticmethod
        def api_request(endpoint):
            url = "https://api.twitch.tv/helix/" + endpoint
            headers = {"Client-ID": twitch_client_id,
                       "Authorization": "Bearer " + twitch_token}
            return requests.get(url, headers=headers)

        def get_followed_list(self):
            followed_list = []
            userid = self.api_request('users').json()['data'][0]['id']
            followed = self.api_request("users/follows?from_id=" + userid + "&first=100")
            for f in followed.json()['data']:
                # print(f['to_id'])
                followed_list.append(f['to_id'])

            return followed_list


    window = MainWindow()
    followers = window.get_followed_list()
    window.show()

    print(followers)

    sys.exit(app.exec_())
