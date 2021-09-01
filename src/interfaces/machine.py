from typing import List
from uuid import UUID

from src.models.db import Execution, Machine


class MachineInterface:

    @staticmethod
    def find_by_simulation(simulation: UUID) -> Machine:
        filters = dict(
            simulation_id=simulation,
        )
        return Machine.objects(**filters).first()

    @staticmethod
    def find_all_by_execution(execution: Execution) -> List[Machine]:
        filters = dict(
            execution=execution,
        )
        return Machine.objects(**filters).all()

    @staticmethod
    def find_one_by_name(name: str) -> Machine:
        filters = dict(
            name=name,
        )
        return Machine.objects(**filters).first()
