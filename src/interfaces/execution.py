from typing import Optional
from uuid import UUID

from src.models.db import Execution


class ExecutionInterface:

    @staticmethod
    def find_one_by_simulation(simulation_uuid: UUID) -> Optional[Execution]:
        filters = dict(
            simulation_id=simulation_uuid
        )
        return Execution.objects(**filters).first()
