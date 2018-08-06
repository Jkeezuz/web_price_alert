import uuid

from src.common.database import Database
import src.models.stores.constants as StoreConstants
import src.models.stores.errors as StoreErrors


class Store(object):
    def __init__(self, name, url_prefix, tag_name, query, _id=None):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.name = name
        self.url_prefix = url_prefix
        self.tag_name = tag_name
        self.query = query

    def __repr__(self):
        return "<Store {}>".format(self.name)

    def get_tag_name(self):
        return self.tag_name

    def get_query(self):
        return self.query

    def json(self):
        return {
            "_id": self._id,
            "name": self.name,
            "url_prefix": self.url_prefix,
            "tag_name": self.tag_name,
            "query": self.query
        }

    @classmethod
    def get_by_id(cls, id):
        return cls(**Database.find_one(StoreConstants.COLLECTION, query={"_id": id}))

    def save_to_mongo(self):
        Database.update(StoreConstants.COLLECTION, { "_id": self._id }, self.json())

    @classmethod
    def get_by_name(cls, name):
        return cls(**Database.find_one(StoreConstants.COLLECTION, {"name": name}))

    @classmethod
    def get_by_url_prefix(cls, url_prefix):
        return cls(**Database.find_one(StoreConstants.COLLECTION, {"url_prefix": {"$regex": '^{}'.format(url_prefix)}}))

    @classmethod
    def get_by_url(cls, url):
        """
        Return a store from a url like "http://www.amazon.com/item/s6nybsy.html
        :param url: item's url
        :return: store or raises a StoreNotFound exception if no store matches the URL
        """
        for i in range(0, len(url)+1):
            try:
                store = cls.get_by_url_prefix(url[:i])
                return store
            except:
                raise StoreErrors.StoreNotFoundException("The URL Prefix used to find a store didn't give any results")

    @classmethod
    def get_all(cls):
        return [cls(**elem) for elem in Database.find(StoreConstants.COLLECTION, {})]

    def delete(self):
        Database.remove(StoreConstants.COLLECTION, {"_id": self._id})
