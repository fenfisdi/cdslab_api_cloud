from time import sleep

import requests

from src.models.db import Machine
from src.models.routes import Simulation


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
