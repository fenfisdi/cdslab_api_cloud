from typing import List, Union
from uuid import UUID

import requests

from src.interfaces import MachineInterface
from src.models.db import Execution, Machine, User
from src.models.routes import Simulation
from .machine import DeleteMachine
from .storage import UploadBucketFile
from ..models.general import MachineStatus


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
            response = requests.post(
                url=url,
                json=data
            )
        except Exception as error:
            print(error)


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
                UploadBucketFile.handle(simulation_uuid, distribution.get("file_id"))

    @classmethod
    def process_complex_distribution(
        cls,
        data: List[dict],
        simulation_uuid: str
    ):
        for element in data:
            for v in element.get("distributions", {}).values():
                UploadBucketFile.handle(simulation_uuid, v.get("file_id"))


class StopMachineSimulation:

    @classmethod
    def handle(cls, execution: Execution):
        print(execution)


class SimulationUseCase:

    @classmethod
    def send_information(cls, machine: Machine, simulation: Simulation):
        url = f"http://{machine.ip}/any_machine"
        try:
            response = requests.get(url, json=simulation.data)
        except Exception as error:
            print(error)
        finally:
            print("Ping")

        try:
            requests.post(url, json=simulation.data)
        except Exception as error:
            print(error)
