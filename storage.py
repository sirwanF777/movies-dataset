import json
from abc import ABC, abstractmethod
from mongo import MongoDatabase


class StorageAbstract(ABC):
    @abstractmethod
    def store(self, data, filename, *args):
        pass


class MongoStore(StorageAbstract):
    def __init__(self):
        self.mongo = MongoDatabase()

    def store(self, datas, collection, *args):
        collection = getattr(self.mongo.database, collection)
        if isinstance(datas, list) and len(datas) > 1:
            # for data in datas:
            collection.insert_mony(datas)
        else:
            collection.insert_one(datas)


class FileStore(StorageAbstract):
    def store(self, datas, filename, *args):
        load_links = list()

        try:
            with open(f"fixtures/{filename}.json", "r") as f:
                load_links = json.loads(f.read())
        except FileNotFoundError:
            pass

        load_links.extend(datas)
        load_links = list(set(load_links))
        with open(f"fixtures/{filename}.json", "w") as f:
            f.write(json.dumps(load_links))
