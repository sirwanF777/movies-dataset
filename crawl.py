import json
import pprint
import requests
from numpy.distutils.command.config import config
from pymongo import MongoClient
from config import STORAGE, NAME_FILE_LINKS_MOVIES, NAME_FILE_INFORMATION_MOVIES
from mongo import MongoDatabase
from storage import FileStore, MongoStore
from multiprocessing import Pool
from threading import Thread
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from parser import AdvertisementPageParser


class CrawlBase(ABC):
    def __init__(self):
        self.storage = self.__set_storage()

    @staticmethod
    def __set_storage():
        if STORAGE == "mongo":
            return MongoStore()
        return FileStore()

    @abstractmethod
    def start(self, store=False):
        pass

    @abstractmethod
    def store(self, datas, filename):
        pass

    @staticmethod
    def get(link):
        try:
            response = requests.get(link)
        except requests.HTTPError:
            return None
        if response.status_code == 200:
            return response
        return None


class LinkCrawler(CrawlBase):
    def __init__(self, url, number_page=1):
        super().__init__()
        self.__links_movie = list()
        self.url = url
        self.number_page = number_page

    def start(self, store=False):
        start_page = 1
        urls = list()
        for i in range(self.number_page):
            urls.append(self.url + str(start_page))
            start_page += 1

        threads = []
        for link in urls:
            tr = Thread(target=self.my_thread, args=(link,))
            threads.append(tr)
            tr.start()

        for i in threads:
            i.join()

        if store:
            self.store(self.__links_movie, NAME_FILE_LINKS_MOVIES)

        print(f"find_links executed successfully -> url: {self.url}.")

    def my_thread(self, link):
        response = self.get(link)
        self.__links_movie.extend(self.find_links(response.text))

    @staticmethod
    def find_links(html_doc):
        soup = BeautifulSoup(html_doc, 'html.parser')
        articles = soup.find_all(
            'div', attrs={'class': 'col mb-3 mb-sm-0 col-sm-auto m-link px-0'}
        )

        links_move = [
            {'link': article.find('a').get('href'), "flag": False} for article in articles
        ]

        return links_move

    def store(self, datas, filename, *args):
        self.storage.store(datas, filename)


class DataCrawler(CrawlBase):
    def __init__(self, search_collection=NAME_FILE_LINKS_MOVIES):
        super().__init__()
        self.__links = self.__load_links(search_collection)
        self.parse = AdvertisementPageParser()
        self._store_bool = None
        self._datas = list()

    def __load_links(self, search_collection):
        links = []

        if STORAGE == "mongo":
            mongodb = MongoDatabase()
            collection = getattr(mongodb.database, search_collection)
            links = self.storage.load(collection)
        elif STORAGE == 'file':
            update_links = []
            with open(f"fixtures/{search_collection}.json", "r") as f:
                links = json.loads(f.read())
                for link in links:
                    if not link["flag"]:
                        link['flag'] = True
                        update_links.append((link["link"], 1))
            with open(f"fixtures/{search_collection}.json", "w") as f:
                f.write(json.dumps(links))
            links = update_links
        if links:
            return links
        return None

    def start(self, store=False):
        self._store_bool = store

        if self.__links:
            threads = []
            for link in self.__links:
                tr = Thread(target=self.__my_multi_processing, args=(link,))
                threads.append(tr)
                tr.start()

            for thread in threads:
                thread.join()

            if self._store_bool and self._datas:
                response = self.store(datas=self._datas)
                print(response)
        else:
            print("There are no links to search")

    def __my_multi_processing(self, link):
        response = self.get(link[0])
        if response is not None:
            data = self.parse.parse(response.text, link)
            self._datas.append(data)

    def store(self, datas, *args):
        if STORAGE == "mongo":
            return self.storage.store(datas, NAME_FILE_INFORMATION_MOVIES)
        elif STORAGE == "file":
            threads = []
            for data in datas:
                tr = Thread(
                    target=self.storage.store,
                    args=(data, data["name"].replace("/", ''))
                )
                threads.append(tr)
                tr.start()

            for tr in threads:
                tr.join()

            return "extract_page executed successfully."
