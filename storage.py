import json
from abc import ABC, abstractmethod

from config import NAME_FILE_LINKS_MOVIES
from mongo import MongoDatabase


class StorageAbstract(ABC):
    @abstractmethod
    def store(self, data, filename, *args):
        pass

    @abstractmethod
    def load(self):
        pass


class MongoStore(StorageAbstract):
    def __init__(self):
        self.mongo = MongoDatabase()

    def store(self, datas, collection, *args):
        collection = getattr(self.mongo.database, collection)
        all_links = [link["link"] for link in collection.find({})]
        update_datas = []
        for data in datas:
            if data["link"] not in all_links:
                update_datas.append(data)

        if update_datas:
            collection.insert_many(update_datas)

        return f"extract_page executed successfully."

    def load(self, collection):
        links = []

        for link in collection.find({"flag": False}):
            collection.update_one({"link": link["link"]},
                                  {"$set": {"flag": True}})
            links.append((link["link"], link["_id"]))

        return links


class FileStore(StorageAbstract):
    def __init__(self):
        self.__load_links = list()

    def store(self, datas, file_name, *args):
        if isinstance(datas, list):
            self.__load_links = self.load(file_name)
            links = [i["link"] for i in self.__load_links]

            # update self.__load_links to datas
            for data in datas:
                if data["link"] not in links:
                    self.__load_links.append(data)

            with open(f"fixtures/{file_name}.json", "w") as f:
                f.write(json.dumps(self.__load_links))
        elif isinstance(datas, dict):
            with open(f"fixtures/adv/{file_name}.json", "w") as f:
                datas.pop('_id')
                f.write(json.dumps(datas))

    def load(self, save_file_name=NAME_FILE_LINKS_MOVIES):
        read_links = list()
        try:
            with open(f"fixtures/{save_file_name}.json", "r") as f:
                read_links = json.loads(f.read())
        except FileNotFoundError:
            pass

        return read_links
