import json
from abc import ABC, abstractmethod

from config import NAME_FILE_LINKS_MOVIES
from mongo import MongoDatabase


class StorageAbstract(ABC):
    @abstractmethod
    def store(self, data, filename, *args):
        pass

    @abstractmethod
    def load(self, file_name):
        pass

    @abstractmethod
    def update_flag_datas(self, file_name, datas):
        pass


class MongoStore(StorageAbstract):
    def __init__(self):
        self.mongo = MongoDatabase()

    def store(self, datas, collection_name, *args):
        collection = getattr(self.mongo.database, collection_name)
        if datas:
            collection.insert_many(datas)

        return f"extract_page executed successfully."

    def load(self, file_name=NAME_FILE_LINKS_MOVIES):
        collection = getattr(self.mongo.database, file_name)
        return [link for link in collection.find({})]

        # links = []
        #
        # for link in self.collection.find({"flag": False}):
        #     self.collection.update_one({"link": link["link"]},
        #                                {"$set": {"flag": True}})
        #     links.append((link["link"], link["_id"]))
        #
        # return links

    def update_flag_datas(self, file_name, datas):
        collection = getattr(self.mongo.database, file_name)
        for data in datas:
            collection.update_one(
                {"_id": data["_id"]},
                {"$set": {"flag": True}}
            )


class FileStore(StorageAbstract):
    def __init__(self):
        self.__load_links = list()

    def store(self, datas: list, file_name, *args):
        if datas and isinstance(datas, list):
            finally_data = datas
            with open(f"fixtures/{file_name}.json", "r") as f:
                finally_data.extend(json.loads(f.read()))

            with open(f"fixtures/{file_name}.json", "w") as f:
                f.write(json.dumps(finally_data))
        elif isinstance(datas, dict):
            with open(f"fixtures/adv/{file_name}.json", "w") as f:
                # self.update_flag_data(NAME_FILE_LINKS_MOVIES, datas)
                f.write(json.dumps(datas))

    def load(self, file_name=NAME_FILE_LINKS_MOVIES):
        read_datas = list()
        try:
            with open(f"fixtures/{file_name}.json", "r") as f:
                read_datas = json.loads(f.read())
        except FileNotFoundError:
            return []

        return read_datas

    def update_flag_datas(self, file_name, datas):
        # pass
        update_data = []
        all_datas = self.load(file_name)
        for data in all_datas:
            if data in datas:
                data["flag"] = True
            update_data.append(data)

        with open(f"fixtures/{file_name}.json", "w") as f:
            f.write(json.dumps(update_data))

    @staticmethod
    def create_id(datas):
        for data in datas:
            data["_id"] = data["link"].split("/")[3]
