import tornado.ioloop
import tornado.web
import tornado.httpserver
from req import RequestHandler
from req import reqenv
from req import Service
import json
import requests
from urllib import parse
import base64
from spotify import SpotifyHandler
from kkbox import KKBOXHandler
from threading import Thread
import time

CLIENT_ID = '70e5f69180f3425c9959eee856311097'
CLIENT_SECRET = '7fdad82fe5a8437a962561a0c09236ed'
USERNAME = 'allenwhale'
KEY = {}

class IndexHandler(RequestHandler):
    @reqenv
    def get(self):
        data = {'scope': 'user-read-private user-read-email playlist-read-private playlist-modify-public playlist-modify-private playlist-read-collaborative', 'state': '1231e', 'redirect_uri': 'http://140.113.90.198:12345/callback', 'client_id': '70e5f69180f3425c9959eee856311097', 'response_type': 'code'}
        url = 'https://accounts.spotify.com/authorize?'+parse.urlencode(data)
        self.redirect(url)
        return

class CallbackHandler(RequestHandler):
    @reqenv
    def get(self):
        print(self.get_argument('code'))
        code = self.get_argument('code')
        url = 'https://accounts.spotify.com/api/token'
        client = base64.standard_b64encode((CLIENT_ID+':'+CLIENT_SECRET).encode()).decode()
        headers = {'Authorization': 'Basic '+client}
        data = {'code': code, 'redirect_uri': 'http://140.113.90.198:12345/callback', 'grant_type': 'authorization_code'}
        r = requests.post(url, headers=headers, data=data)
        print(r.text)
        global KEY
        KEY = json.loads(r.text)
        print('key', KEY)
        update()
        return

    @reqenv
    def post(self):
        print('post',self.request)
        return

def shutdown():
    srv.stop()
    tornado.ioloop.IOLoop.instance().stop()

def _start():
    print('prepare')
    time.sleep(5)
    print('start')
    r = requests.get('http://localhost:12345', allow_redirects=True)
    print(r.status_code, r.text)
    print('end')

URLS = ['http://www.kkbox.com/tw/tc/charts/overall_newrelease-daily-song-latest.html',
        'http://www.kkbox.com/tw/tc/charts/chinese-daily-song-latest.html',
        'http://www.kkbox.com/tw/tc/charts/chinese-newrelease_daily-song-latest.html',
        'http://www.kkbox.com/tw/tc/charts/western-daily-song-latest.html',
        'http://www.kkbox.com/tw/tc/charts/western-newrelease_daily-song-latest.html'
        ]
PLAYLIST = ['7fjEesue7CYHiJaPhbCLEf',
        '3LbXl2SK6mc4MuULUXfI8p',
        '5ohKlAhooYvbuTlEwHasfF',
        '4uEcAXBFgch5n4r1WCHjjC',
        '2cb8oJBjC03StlDXFJcbs3']

def update():
    print(KEY)
    s = SpotifyHandler(CLIENT_ID, CLIENT_SECRET, USERNAME, KEY)
    for url, playlist in zip(URLS, PLAYLIST):
        p = s.playlist(playlist)[1]
        p.remove_all()
        k = KKBOXHandler(url)
        l = k.parse()
        for song in l:
            print(song)
            res = s.search(song['song']+' '+song['songer'])
            if res:
                p.add_tracks([res['uri']])


if __name__ == '__main__':
#    Thread(target=_start).start()
    print('app')
    app = tornado.web.Application([
        ('/', IndexHandler),
        ('/callback', CallbackHandler),
        ('/callback/', CallbackHandler),
        ])
    global srv
    srv = tornado.httpserver.HTTPServer(app)
    srv.listen(12345)
    tornado.ioloop.IOLoop().instance().start()
