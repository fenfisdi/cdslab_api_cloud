from mongoengine import (
    BooleanField,
    DateTimeField,
    EnumField,
    ReferenceField,
    StringField,
    UUIDField
)

from src.models.general import MachineStatus
from .base import BaseDocument
from .user import User


class Machine(BaseDocument):
    name = StringField()
    user = ReferenceField(User, dbref=True)
    simulation_id = UUIDField(binary=False)
    ip = StringField()
    creation_at = DateTimeField()
    gcp_id = StringField(unique=True)
    zone = StringField()
    status = EnumField(MachineStatus)
    is_deleted = BooleanField(default=False)
    deleted_at = DateTimeField(null=True)
