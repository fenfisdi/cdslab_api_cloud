from time import sleep
from typing import List, Union
from uuid import UUID

import requests

from src.models.db import Execution, Machine, User
from src.models.routes import Simulation
from .storage import UploadBucketFile
from ..interfaces import MachineInterface


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
            print(machine.ip)

    @classmethod
    def send_information(cls, data: dict, ip: str):
        endpoint = "/endpoint"
        url = f"http://{ip}"
        try:
            response = requests.post(
                "/".join([url, endpoint]),
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
        print(url)
        sleep(10)
        try:
            response = requests.get(url, json=simulation.data)
        except Exception as error:
            print(error)
        finally:
            print("Ping")

        try:
            response = requests.post(url, json=simulation.data)
            print(response.json())
        except Exception as error:
            print(error)
