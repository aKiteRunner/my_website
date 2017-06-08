import requests
import re
import time
import datetime
from .models import *
from bs4 import BeautifulSoup


def init_movie(URLS):
    init_javbus_censored(URLS['javbus_censored'])
    init_javbus_uncensored(URLS['javbus_uncensored'])
    init_javbus_euro(URLS['javbus_euro'])


def init_javbus_censored(url, pages=30, sleep_second=5):
    pattern = re.compile(r'(.*)? / (\d+-\d+-\d+)')
    for page in range(pages):
        time.sleep(sleep_second)
        html = requests.get('{}/page/{}'.format(url, page)).text
        bs = BeautifulSoup(html, 'lxml')
        for a in bs.findAll('a', {'class': 'movie-box'}):
            for span in a.findAll('span'):
                img = a.find('img')['src']
                text = span.get_text().split('\n')
                title = text[0]
                match = pattern.match(text[-1])
                number, date = match.group(1), match.group(2)
                movie_url = '{}/{}'.format(url, number)
                date = datetime.datetime.strptime(date, '%Y-%m-%d')
                Movie.objects.create(image_url=img, movie_url=movie_url, title=title, number=number, date=date)


def init_javbus_uncensored(url):
    pass


def init_javbus_euro(url):
    pass


def get_pages(total_page, cur_page):
    pages = [i + 1 for i in range(total_page)]
    if cur_page > 1:
        pre_page = cur_page - 1
    else:
        pre_page = 1
    if cur_page < total_page:
        next_page = cur_page + 1
    else:
        next_page = total_page
    if cur_page <= 2:
        pages = pages[:5]
    elif total_page - cur_page <= 2:
        pages = pages[-5:]
    else:
        pages = filter(lambda x: abs(x - cur_page) <= 2, pages)
    return pages, pre_page, next_page