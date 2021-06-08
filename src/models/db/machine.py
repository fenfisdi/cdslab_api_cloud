from mongoengine import DateTimeField, ReferenceField, StringField

from .base import BaseDocument
from .user import User


class Machine(BaseDocument):
    name = StringField()
    user = ReferenceField(User, dbref=True)
    ip = StringField()
    creation_at = DateTimeField()
    gcp_id = StringField(unique=True)
    zone = StringField()
