from enum import Enum


class MachineStatus(Enum):
    CREATED: str = 'created'
    DELETED: str = 'deleted'
    FINISHED: str = 'finished'
    RUNNING: str = 'running'
    ERROR_EMERGENCY: str = 'stop by internal error'
