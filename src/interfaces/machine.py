from uuid import UUID

from src.models.db import Machine, User


class MachineInterface:

    @staticmethod
    def find_one(user: User) -> Machine:
        filters = dict(
            user=user,
            is_deleted=False,
        )
        return Machine.objects(**filters).first()

    @staticmethod
    def find_by_simulation(simulation: UUID):
        filters = dict(
            simulation_id=simulation,
        )
        return Machine.objects(**filters).first()
