from mongoengine import StringField

from .base import BaseDocument


class User(BaseDocument):
    name = StringField()
    email = StringField(unique=True, required=True)
