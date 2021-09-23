from typing import List, Union
from uuid import UUID

import requests

from src.interfaces import MachineInterface
from src.models.db import Execution, User
from src.models.general import MachineStatus
from src.models.routes import Simulation
from .machine import DeleteMachine
from .storage import UploadBucketFile


class CreateExecution:

    @classmethod
    def handle(cls, simulation: Simulation, user: User) -> Execution:
        execution = Execution(
            user=user,
            simulation_id=simulation.simulation_id,
        )
        try:
            execution.save()
            return execution
        except Exception as error:
            raise RuntimeError(error)


class SendSimulationData:

    @classmethod
    def handle(cls, simulation: Simulation, execution: Execution):
        machines = MachineInterface.find_all_by_execution(execution)
        for machine in machines:
            cls._send_information(simulation.data, machine.ip)

    @classmethod
    def _send_information(cls, data: dict, ip: str):
        url = f"http://{ip}/execute"
        try:
            requests.post(
                url=url,
                json=data
            )
        except Exception:
            pass


class ProcessInformation:

    @classmethod
    def handle(cls, data: dict, simulation_uuid: Union[UUID, str]) -> bool:
        simulation_uuid = str(simulation_uuid)

        try:
            # Upload files from susceptibility and mobility groups
            [
                cls.process_basic_distribution(
                    element,
                    simulation_uuid
                ) for element in [
                    data.get("susceptibility_groups"),
                    data.get("mobility_groups")
                ]
            ]

            # Upload files from disease groups and natural history
            [
                cls.process_complex_distribution(
                    element,
                    simulation_uuid
                ) for element in [
                    data.get("disease_groups"), data.get("natural_history")
                ]
            ]
            return True
        except Exception:
            return False

    @classmethod
    def process_basic_distribution(cls, data: List[dict], simulation_uuid: str):
        for element in data:
            distribution_base = ["weights", "empirical"]
            distribution = element.get("distribution")
            if distribution.get("type") in distribution_base:
                UploadBucketFile.handle(
                    simulation_uuid,
                    distribution.get("file_id")
                )

    @classmethod
    def process_complex_distribution(
        cls,
        data: List[dict],
        simulation_uuid: str
    ):
        for element in data:
            for v in element.get("distributions", {}).values():
                UploadBucketFile.handle(simulation_uuid, v.get("file_id"))


class VerifySimulation:

    @classmethod
    def handle(cls, execution: Execution):
        machines = MachineInterface.find_all_by_execution(execution)
        machine_status = [machine.status for machine in machines]
        if MachineStatus.FINISHED in machine_status:
            # TODO: FINISH SUCCESSFULL
            pass
        else:
            # TODO: EXECUTION ERROR
            pass


class StopSimulationExecution:

    @classmethod
    def handle(
        cls,
        execution: Execution,
        name: str,
        emergency: bool = False
    ) -> bool:
        machine = MachineInterface.find_one_by_name(name)
        try:
            machine.update(status=MachineStatus.FINISHED)

            if not machine:
                return True
            is_invalid = DeleteMachine.handle(machine.name, machine.zone)
            if is_invalid:
                return True

            if emergency:
                machine.update(status=MachineStatus.ERROR_EMERGENCY)
            else:
                machine.update(status=MachineStatus.DELETED)
            machine.reload()

            VerifySimulation.handle(execution)
        except Exception:
            return True

        return False
