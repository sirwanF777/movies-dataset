from pymongo import MongoClient


class MongoDatabase:
    instance = None

    @classmethod
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(*args, **kwargs)
        return cls.instance

    def __init__(self):
        self.client = MongoClient("localhost", 27017)
        self.database = self.client["crawler"]

    @property
    def get_database(self):
        return self.database
