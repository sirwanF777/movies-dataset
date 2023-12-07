import sys
import urllib.request
from multiprocessing import Pool
from threading import Thread

import requests

from config import OBJECT_CLASS, NAME_FILE_LINKS_MOVIES
from crawl import LinkCrawler, DataCrawler, ImageDownloader


def my_pool(link):
    url, page_number = link
    crawler = LinkCrawler(url=url, number_page=page_number)
    crawler.start(store=True)


def start_find_links():
    url = "https://www.f2m.top/category/{}/page/"
    links = []
    number_pages = 10

    while True:
        try:
            number_pages = int(input(f"enter number of page (1-10): "))
        except ValueError as ex:
            print(f"ERROR!!!\n{ex}\n\t-> please enter integer.\n{'--'*20}")
            continue

        if number_pages in range(1, 11):
            break
        else:
            print(f"enter number page in range (1 to 10).\n{'--'*20}")

    for genre in OBJECT_CLASS.values():
        links.append([url.format(genre), number_pages])

    pool = Pool(2)
    with pool:
        pool.map(my_pool, links)


def check_internet_connection():
    try:
        response = requests.get("https://www.f2m.top/")
        return True
    except requests.exceptions.ConnectionError:
        return False


if __name__ == "__main__":
    """
    By running the program, we must give it input in the terminal, which is in 
    the following two ways:
    1: python mian.py find_links
    2: python mian.py extract_page
    
    find_links searches for the link of each web page for the movie and
    saves it according to the STORAGE in the config file or as a file or as
    mongodb (NoSQL) in the server: localhost, port: 27017.
    
    
    """
    switch = sys.argv[1]
    if switch == "find_links":
        if check_internet_connection():
            start_find_links()
        else:
            print("Internet is not connected.")
    elif switch == "extract_page":
        if check_internet_connection():
            data = DataCrawler()
            data.start(store=True)
        else:
            print("Internet is not connected.")
    elif switch == "image_downloader":
        if check_internet_connection():
            data = ImageDownloader()
            data.start(store=True)
        else:
            print("Internet is not connected.")
