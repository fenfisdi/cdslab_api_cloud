from time import sleep

import requests

from src.models.db import Execution, Machine, User
from src.models.routes import Simulation


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
