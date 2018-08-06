import re
import uuid

import requests
from bs4 import BeautifulSoup

from src.common.database import Database
import src.models.items.constants as ItemConstants
from src.models.stores.store import Store


class Item(object):
    def __init__(self, name, url, price = None, _id=None):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.name = name
        self.url = url
        store = Store.get_by_url(url)
        self.tag_name = store.get_tag_name()
        self.query = store.get_query()
        self.price = price

    def __repr__(self):
        return "<Item {} with URL {} and price {}>".format(self.name, self.url, self.price)

    @classmethod
    def get_by_id(cls, item_id):
        return cls(**Database.find_one(ItemConstants.COLLECTION, {"_id": item_id}))

    def load_price(self):
        request = requests.get(self.url)
        content = request.content
        soup = BeautifulSoup(content, "html.parser")
        element = soup.find(self.tag_name, self.query)
        string_price = element.text.strip()
        string_price = ''.join(string_price.split())
        pattern = re.compile("(\d+.\d+)")
        if pattern is None:
            pattern = re.compile("\d \d+\.\d")
        if pattern is None:
            pattern = re.compile("\d+ \d+")
        match = pattern.search(string_price)
        self.price = float(match.group())
        return self.price

    def save_to_mongo(self):
        Database.update(ItemConstants.COLLECTION, query= {'_id': self._id }, data=self.json())

    def json(self):
        return {
            "_id": self._id,
            "name": self.name,
            "url": self.url,
            "price": self.price
        }