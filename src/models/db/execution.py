from mongoengine import EnumField, ReferenceField, StringField, UUIDField

from src.models.general import ExecutionStatus
from .base import BaseDocument
from .user import User


class Execution(BaseDocument):
    user = ReferenceField(User, dbref=True, required=True)
    simulation_id = UUIDField(binary=False, required=True)
    status = EnumField(ExecutionStatus, default=ExecutionStatus.CREATED)
    execution_time = StringField(null=True)
