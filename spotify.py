import requests
import json
import base64
from urllib import parse

class SpotifyHandler:
    def __init__(self, client_id, client_secret, username, KEY):
        self._client_id = client_id
        self._client_secret = client_secret
        self._username = username
        self._token_type = KEY['token_type']
        self._access_token = KEY['access_token']
        self._refresh_token = KEY['refresh_token']
        self._expires_in = KEY['expires_in']
        self._headers = None
        self._baseurl = 'https://api.spotify.com/v1/'

    def gen_headers(self):
        self._headers = {'Authorization': self._token_type+' '+self._access_token}
        return self._headers

    def refresh(self):
        client = base64.standard_b64encode((self._client_id+':'+self._client_secret).encode()).decode()
        headers = {'Authorization': 'Basic '+client}
        data = {'grant_type': 'refresh_token', 'refresh_token': self._refresh_token}
        url = 'https://accounts.spotify.com/api/token'
        r = requests.post(url, headers=headers, data=data)
        meta = json.loads(r.text)
        self._access_token = meta['access_token']


    def login(self):
        client = base64.standard_b64encode((self._client_id+':'+self._client_secret).encode()).decode()
        headers = {'Authorization': 'Basic '+client}
        data = {'grant_type': 'client_credentials'}
        r = requests.post('https://accounts.spotify.com/api/token', headers = headers, data = data)
        if int(r.status_code) != 200:
            return (json.loads(r.text), None)
        meta = json.loads(r.text)
        self._access_token = meta['access_token']
        self._token_type = meta['token_type']
        self._headers = {'Authorization': self._token_type+' '+self._access_token}
        return (None, self._access_token)

    def playlists(self):
        url = self._baseurl + 'users/' + self._username + '/playlists'
        r = requests.get(url, headers = self.gen_headers())
        meta = json.loads(r.text)
        items = meta['items']
        return (None, items)
    
    class Playlist:
        def __init__(self, playlist, srv):
            self._playlist = playlist
            self._playlist_id = self._playlist['id']
            self.srv = srv

        def tracks(self):
            return self._playlist['tracks']['items']

        def remove_all(self):
            tracks = self.tracks()
            t_tracks = []
            for t in tracks:
                print(t)
                t_tracks.append({'uri': t['track']['uri']})

            self.remove_tracks(t_tracks)

        def remove_tracks(self, tracks=[]):
            headers = self.srv.gen_headers()
            headers.update({'Content-Type': 'application/json'})
            data = json.dumps({'tracks': tracks})
            print(data)
            print(headers)
            url = self.srv._baseurl + 'users/' + self.srv._username + '/playlists/' + self._playlist_id + '/tracks'
            r = requests.delete(url, headers = headers, data = data)
            print(r.status_code)
            print(r.text)
            print(r.headers)
            return 

        def add_tracks(self, tracks=[]):
            headers = self.srv.gen_headers()
            headers.update({'Content-Type': 'application/json'})
            data = json.dumps({'uris': tracks})
            url = self.srv._baseurl + 'users/' + self.srv._username + '/playlists/' + self._playlist_id + '/tracks'
            r = requests.post(url, headers = headers, data = data)
            print(r.status_code)
            print(r.text)


    def playlist(self, playlist_id):
        url = self._baseurl + 'users/' + self._username + '/playlists/' + playlist_id
        r = requests.get(url, headers = self.gen_headers())
        meta = json.loads(r.text)
        return (None, self.Playlist(meta, self)) 

    def search(self, query=''):
        headers = self.gen_headers()
        data = {'q': query, 'type':'track'}
        url = 'https://api.spotify.com/v1/search?'
        r = requests.get(url+parse.urlencode(data))
        meta = json.loads(r.text)
        try:
            return (meta['tracks']['items'][0])
        except:
            return None


    def me(self):
        url = 'https://api.spotify.com/v1/me'
        r = requests.get(url, headers = self.gen_headers())
        print(r.status_code)
        print(r.text)

