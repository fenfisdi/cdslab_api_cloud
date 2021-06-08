from src.models.db import Machine, User


class MachineInterface:

    @staticmethod
    def find_one(user: User) -> Machine:
        filters = dict(
            user=user
        )
        return Machine.objects(**filters).first()
