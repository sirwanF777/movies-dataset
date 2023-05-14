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
    def update_flag(self, file_name, datas):
        pass


class MongoStore(StorageAbstract):
    def __init__(self):
        self.mongo = MongoDatabase()

    def store(self, datas, collection_name, *args):
        """
        takes (data) in its input and stores it in (collection_neme) which is the
        collection name of the database defined in (mongo.py).

        :param datas: Gets a list of data where each data is defined as dict().
        :param collection_name: The name of the collection in the desired
               database (defined in the mongo.py file) where the (datas) is stored.
        """

        collection = getattr(self.mongo.database, collection_name)
        if datas:
            collection.insert_many(datas)

        return f"extract_page executed successfully."

    def load(self, collection_name=NAME_FILE_LINKS_MOVIES, filter_data=None):
        """
        By taking the name of a collection, this function finds all its information
        (collection) in the desired database and returns it in the form of a list.

        :param collection_name: collection name in database.
        :return: A list of all the data in the collection (file_name).
        """
        # collection = getattr(self.mongo.database, file_name)
        collection = self.mongo.database.get_collection(collection_name)
        if filter_data:
            data = collection.find(filter_data)
        else:
            data = collection.find()

        return [link for link in data]

    def update_flag(self, file_name, datas):
        """
        By getting the information of each link (movies_links), it has an item
        called (flag) which is equal to (false) by default, which means that the
        information of this link has not been taken yet.

        After searching the information of that link, the job of this function is
        to set the value of the (flag) to equal (correct) in order not to search
        for a duplicate link again later.

        :param file_name: collection name in database.
        :param datas: Data to be updated.
        :return: None
        """
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
        """
        This function in the FileStore class takes an input named (datas) of type list,
        where each member of the list is a dict().
        It stores this information in a file (json.file_name). (file_name is taken in
        the input)

        :param datas: Gets a list of data where each data is defined as dict().
        :param file_name: The name of a file in which the (datas) is to be stored.
        """
        if datas and isinstance(datas, list):
            finally_data = datas
            with open(f"fixtures/{file_name}.json", "r") as f:
                finally_data.extend(json.loads(f.read()))

            with open(f"fixtures/{file_name}.json", "w") as f:
                f.write(json.dumps(finally_data))
        elif isinstance(datas, dict):
            with open(f"fixtures/adv/{file_name}.json", "w") as f:
                f.write(json.dumps(datas))

    def load(self, file_name=NAME_FILE_LINKS_MOVIES, filter_data=None):
        """
        By taking the name of a collection, this function finds all its information
        (collection) in the desired database and returns it in the form of a list.

        :param file_name: The name of the file whose information should be loaded.
        :return: A list of all the data in the (file_name).
        """
        try:
            with open(f"fixtures/{file_name}.json", "r") as f:
                all_datas = json.loads(f.read())
        except FileNotFoundError:
            return []

        if filter_data:
            new_datas = [
                data for data in all_datas if filter_data.items() <= data.items()
            ]
        else:
            return all_datas

        return new_datas

    def update_flag(self, file_name, datas):
        """
        By getting the information of each link (movies_links), it has an item
        called (flag) which is equal to (false) by default, which means that the
        information of this link has not been taken yet.

        After searching the information of that link, the job of this function is
        to set the value of the (flag) to equal (correct) in order not to search
        for a duplicate link again later.

        :param file_name: The name of the file containing the link of the movies.
        :param datas: Data to be updated.
        :return: None
        """
        update_data = []
        all_datas = self.load(file_name)
        for data in all_datas:
            if data in datas:
                data["flag"] = True
            update_data.append(data)

        with open(f"fixtures/{file_name}.json", "w") as f:
            f.write(json.dumps(update_data))

    # @staticmethod
    # def create_post_id(datas):
    #     """
    #     At this time, it does not automatically insert data (_id) in the data stored
    #     in the file with the extension (.json), but in the data stored in mongoDB,
    #     this operation is done automatically. In order for the information inside
    #     (movies_links) both in (.json) file and in NoSQL file to have three
    #     attributes: 1:_id 2: link 3: flag, it must be saved as file (.json), attribute
    #     (_id) value set manually.
    #     Here, each link within itself is a special code that we can use for (_id).
    #
    #     :param datas: This function takes a list of data as dict() as input.
    #     :return: None (This is a public function and changes the original data).
    #     """
    #     for data in datas:
    #         data["_id"] = data["link"].split("/")[3]
