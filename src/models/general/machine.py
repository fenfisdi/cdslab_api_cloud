from enum import Enum


class MachineStatus(Enum):
    CREATED: str = 'created'
    DELETED: str = 'deleted'
    FINISHED: str = 'finished'
    ERROR_EMERGENCY: str = 'stop by internal error'
