from os import environ

from mongoengine import connect

from src.utils.patterns import Singleton


class MongoEngine(metaclass=Singleton):
    def __init__(self):
        self.mongo_uri = environ.get('MONGO_URI')

    def register_connection(self):
        return connect(host=self.mongo_uri)
