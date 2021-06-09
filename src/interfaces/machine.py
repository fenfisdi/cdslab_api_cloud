from src.models.db import Machine, User


class MachineInterface:

    @staticmethod
    def find_one(user: User) -> Machine:
        filters = dict(
            user=user,
            is_deleted=False,
        )
        return Machine.objects(**filters).first()
