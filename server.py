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
        shutdown()
        return

    @reqenv
    def post(self):
        print('post',self.request)
        return

def shutdown():
    srv.stop()
    tornado.ioloop.IOLoop.instance().stop()

URLS = ['http://www.kkbox.com/tw/tc/charts/overall_newrelease-daily-song-latest.html']
PLAYLIST = ['78g9F2Sv2LVp6lGjbl4ydD']

if __name__ == '__main__':
    app = tornado.web.Application([
        ('/', IndexHandler),
        ('/callback', CallbackHandler),
        ('/callback/', CallbackHandler),
        ('/(.*)', tornado.web.StaticFileHandler, {'path': '../html'}),
        ])
    global srv
    srv = tornado.httpserver.HTTPServer(app)
    srv.listen(12345)
    tornado.ioloop.IOLoop().instance().start()
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
