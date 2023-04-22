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
        if isinstance(datas, list):
            collection.insert_many(datas)
        else:
            collection.insert_one(datas)

        return f"extract_page executed successfully."


class FileStore(StorageAbstract):
    def store(self, datas, filename, *args):
        if isinstance(datas, list):
            load_links = list()

            try:
                with open(f"fixtures/{filename}.json", "r") as f:
                    load_links = json.loads(f.read())
            except FileNotFoundError:
                pass
            links = [i["link"] for i in load_links]

            for data in datas:
                if data["link"] not in links:
                    load_links.append(data)

            with open(f"fixtures/{filename}.json", "w") as f:
                f.write(json.dumps(load_links))
        elif isinstance(datas, dict):
            with open(f"fixtures/adv/{filename}.json", "w") as f:
                datas.pop('_id')
                f.write(json.dumps(datas))
