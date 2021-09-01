from enum import Enum


class ExecutionStatus(Enum):
    CREATED: str = 'created'
    RUNNING: str = 'running'
    FAILED: str = 'failed'
