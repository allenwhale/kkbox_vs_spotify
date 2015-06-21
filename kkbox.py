import requests
from bs4 import BeautifulSoup as bs

class KKBOXHandler:
    def __init__(self, url):
        self._url = url
        self._doc = requests.get(self._url).text
        self._soup = bs(self._doc)

    def parse(self):
        tracks = self._soup.find('div', class_='charts-top100').find('table').find('tbody').find_all('tr')
        res = []
        for t in tracks:
            song = t.find_all('td')[2].find('div').find('a')['title']
            singer = t.find_all('td')[2].find('div').find('h5').find('a')['title']
            res.append({'song': song.split()[0], 'songer': singer.split()[0]})

        return res

if __name__ == '__main__':
    k = KKBOXHandler('http://www.kkbox.com/tw/tc/charts/overall_newrelease-daily-song-latest.html')
    print(k.parse())
