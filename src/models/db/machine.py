from mongoengine import (
    BooleanField,
    DateTimeField,
    EnumField,
    ReferenceField,
    StringField
)

from src.models.general import MachineStatus
from .base import BaseDocument
from .execution import Execution


class Machine(BaseDocument):
    execution = ReferenceField(Execution, dbref=True)
    name = StringField()
    ip = StringField()
    creation_at = DateTimeField()
    gcp_id = StringField(unique=True)
    zone = StringField()
    status = EnumField(MachineStatus)
    is_deleted = BooleanField(default=False)
    deleted_at = DateTimeField(null=True)
