import datetime
import uuid
from email.message import EmailMessage
import smtplib
import src.models.alerts.constants as AlertConstants
import requests
from src.common.database import Database
from src.models.items.item import Item


class Alert(object):
    def __init__(self, user_email, price_limit, item_id, active=True, last_checked = None,  _id=None):
        self._id = uuid.uuid4().hex if _id is None else _id
        self.user_email = user_email
        self.price_limit = price_limit
        self.last_checked = datetime.datetime.utcnow() if last_checked is None else last_checked
        self.item = Item.get_by_id(item_id)
        self.active = active

    def __repr__(self):
        return "<Alert for {} on item {} with price {}>".format(self.user_email, self.item.name, self.price_limit)


    def send(self):
        email = EmailMessage()
        email['Subject'] = AlertConstants.SUBJECT
        email['From'] = AlertConstants.EMAIL_ADDRESS
        email['To'] = self.user_email
        email.set_content('Your item {} is at price {} (price alert set at '
                          'price lower than {})'
                          ''
                          '\nLINK: {}'.format(self.item.name, self.item.price, self.price_limit, self.item.url))
        s = smtplib.SMTP(host='smtp.gmail.com', port=587)
        s.starttls()
        s.login(AlertConstants.EMAIL_ADDRESS, AlertConstants.PASSWORD)
        s.send_message(email)
        s.quit()

    def alert(self):
        self.send()

    @classmethod
    def find_needing_update(cls, minutes_since_update = AlertConstants.ALERT_TIMEOUT ):
        last_updated_limit = datetime.datetime.utcnow() - datetime.timedelta(minutes=minutes_since_update)
        return [cls(**elem) for elem in Database.find(AlertConstants.COLLECTION, {"last_checked":
                                                                                      {"$lte": last_updated_limit},
                                                                                  "active": True
                                                                                  })]

    def save_to_mongo(self):
        Database.update(AlertConstants.COLLECTION, {"_id": self._id}, self.json())

    def json(self):
        return {
            "_id": self._id,
            "price_limit": self.price_limit,
            "last_checked": self.last_checked,
            "user_email": self.user_email,
            "item_id": self.item._id,
            "active": self.active
        }

    def load_item_price(self):
        self.item.load_price()
        self.last_checked = datetime.datetime.utcnow()
        self.item.save_to_mongo()
        self.save_to_mongo()
        return self.item.price

    def alert_user(self):
        if self.item.price < self.price_limit:
            self.alert()

    @classmethod
    def find_by_id(cls, alert_id):
        return cls(**Database.find_one(AlertConstants.COLLECTION, {"_id": alert_id}))

    @classmethod
    def find_by_user_email(cls, email):
        return [cls(**elem) for elem in Database.find(AlertConstants.COLLECTION, {"user_email": email})]

    def deactivate(self):
        self.active = False
        self.save_to_mongo()

    def activate(self):
        self.active = True
        self.save_to_mongo()

    def delete(self):
        Database.remove(AlertConstants.COLLECTION, {'_id': self._id})

