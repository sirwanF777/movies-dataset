import requests
from config import STORAGE, NAME_FILE_LINKS_MOVIES, NAME_FILE_INFORMATION_MOVIES
from storage import FileStore, MongoStore
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
        links = self.find_links(response.text)
        self.__links_movie.extend(links)

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

    def store(self, datas, file_name, *args):
        # # if isinstance(self.storage, FileStore):
        # self.storage.create_post_id(datas)
        new_datas = self.update_links(datas)
        self.storage.store(new_datas, file_name)

    def update_links(self, datas):
        all_links = list()
        for link in self.storage.load(NAME_FILE_LINKS_MOVIES):
            all_links.append(link["link"])

        new_datas = [data for data in datas if data["link"] not in all_links]

        return new_datas


class DataCrawler(CrawlBase):
    def __init__(self, search_collection=NAME_FILE_LINKS_MOVIES):
        super().__init__()
        self.__datas = self.__load_links(search_collection)
        self.parse = AdvertisementPageParser()
        self._store_bool = None
        self._datas = list()

    def __load_links(self, search_collection):
        datas = self.storage.load(search_collection, filter_data={"flag": False})
        return datas

    def start(self, store=False):
        self._store_bool = store

        if self.__datas:
            threads = []
            for data in self.__datas:
                tr = Thread(target=self.__my_multi_processing, args=(data,))
                threads.append(tr)
                tr.start()

            for thread in threads:
                thread.join()

            self.storage.update_flag(NAME_FILE_LINKS_MOVIES, self.__datas)

            if self._store_bool and self._datas:
                response = self.store(datas=self._datas)
                print(response)
        else:
            print("There are no links to search")

    def __my_multi_processing(self, data):
        response = self.get(data["link"])
        if response is not None:
            data = self.parse.parse(response.text, data)
            self._datas.append(data)

    def store(self, datas, *args):
        if datas and STORAGE == "mongo":
            return self.storage.store(datas, NAME_FILE_INFORMATION_MOVIES)
        elif STORAGE == "file":
            threads = []
            for data in datas:
                tr = Thread(
                    target=self.storage.store,
                    args=(data, data["_id"])
                )
                threads.append(tr)
                tr.start()

            for tr in threads:
                tr.join()

            return "extract_page executed successfully."


class ImageDownloader(CrawlBase):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.all_datas = self.get_all_datas()

    def get_all_datas(self):
        datas = self.storage.load(NAME_FILE_INFORMATION_MOVIES)

        return datas

    def start(self, store=True):
        for data in self.all_datas:
            response = self.get(data['img_links'])
            self.store(response, data['post_id'])

    @staticmethod
    def get(link):
        try:
            response = requests.get(link, stream=True)
        except requests.HTTPError:
            return None
        if response.status_code == 200:
            return response
        return None

    def store(self, response, filename):
        with open(f"fixtures/images/{filename}.jpg", "ab") as f:
            f.write(response.content)
            for _ in response.iter_lines():
                f.write(response.content)
