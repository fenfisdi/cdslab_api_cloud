import re
from datetime import datetime
from json import loads
from os import environ
from subprocess import PIPE, STDOUT, run
from typing import Optional, Tuple
from uuid import uuid1

from requests import Session
from requests.adapters import HTTPAdapter
from unidecode import unidecode
from urllib3 import Retry

from src.models.db import Execution, Machine as DBMachine, User
from src.models.general import MachineStatus
from src.models.routes.machine import Machine, Simulation


class CreateMultipleMachines:

    @classmethod
    async def handle(
        cls,
        simulation: Simulation,
        execution: Execution,
        user: User
    ):
        project = environ.get('GCP_PROJECT')
        list_machines = []
        for _ in range(simulation.machine.instances):
            information, is_invalid = cls.create_machine(
                user,
                project,
                simulation.machine
            )

            if not is_invalid:
                new_machine = await cls._save_information_machine(
                    information,
                    execution
                )
                list_machines.append(new_machine)
                cls._test_ip_machine(new_machine)

    @classmethod
    def create_machine(
        cls,
        user: User,
        project: str,
        machine: Machine
    ) -> Tuple[Optional[dict], bool]:
        service_account = environ.get('GCP_SERVICE_ACCOUNT')
        container = environ.get('GCP_CONTAINER')

        command = f'gcloud compute instances ' \
                  f'create-with-container {cls._get_machine_name(user.name)} ' \
                  f'--project={project} ' \
                  f'--zone=us-east1-c ' \
                  f'--machine-type={cls._create_spec_machine(machine)} ' \
                  f'--subnet=default ' \
                  f'--network-tier=PREMIUM ' \
                  f'--metadata=google-logging-enabled=true ' \
                  f'--maintenance-policy=TERMINATE ' \
                  f'--service-account={service_account} ' \
                  f'--scopes {cls._get_cloud_scopes()} ' \
                  f'--tags=http-server ' \
                  f'--image=cos-89-16108-403-26 ' \
                  f'--image-project=confidential-vm-images ' \
                  f'--boot-disk-size=10GB ' \
                  f'--boot-disk-type=pd-standard ' \
                  f'--boot-disk-device-name=vm-cdslib-poc-10538278323-exid01 ' \
                  f'--no-shielded-secure-boot ' \
                  f'--shielded-vtpm ' \
                  f'--shielded-integrity-monitoring ' \
                  f'--format=json ' \
                  f'--verbosity=error ' \
                  f'--container-env={cls._get_container_env()} ' \
                  f'--container-image={container}'

        return cls.run_command(command)

    @classmethod
    def _get_machine_name(cls, name: str) -> str:
        user_name = unidecode(name.replace(" ", "").lower())
        return '-'.join([user_name, uuid1().hex])

    @classmethod
    def _get_container_env(cls) -> str:
        container_env = {
            "HOST": "0.0.0.0",
            "PORT": 80,
            "CLOUD_API": environ.get("CLOUD_API"),
        }

        return ",".join([f"{k}={v}" for k, v in container_env.items()])

    @classmethod
    def _get_cloud_scopes(cls) -> str:
        scopes = [
            'https://www.googleapis.com/auth/devstorage.read_only',
            'https://www.googleapis.com/auth/logging.write',
            'https://www.googleapis.com/auth/monitoring.write',
            'https://www.googleapis.com/auth/servicecontrol',
            'https://www.googleapis.com/auth/service.management.readonly',
            'https://www.googleapis.com/auth/trace.append'
        ]
        return ",".join(scopes)

    @classmethod
    def run_command(cls, command: str) -> Tuple[Optional[dict], bool]:
        out = run(command.split(" "), stdout=PIPE, stderr=STDOUT)
        if out.returncode != 0:
            return None, True
        return cls._decode_success_message(out.stdout), False

    @classmethod
    def _decode_success_message(cls, message: bytes) -> dict:
        split_message = message.split(b'\n')
        json_message = b'\n'.join(split_message[1:])
        try:
            return loads(json_message.decode('utf-8'))[0]
        except Exception as error:
            raise Exception(error)

    @classmethod
    def _create_spec_machine(cls, machine: Machine) -> str:
        return f'n2-custom-{machine.cpu}-{machine.memory}'

    @classmethod
    def _test_ip_machine(cls, machine: DBMachine):
        try:
            session = Session()
            retry = Retry(connect=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            response = session.post(
                url=f"http://{machine.ip}/testing",
            )
        except Exception as error:
            print(error)

    @classmethod
    async def _save_information_machine(
        cls,
        information: dict,
        execution: Execution
    ) -> DBMachine:
        zone_regex = r"(us-[a-z1-9A-Z]{3,8}-.$)"
        zone = information.get('zone')
        zone = re.search(zone_regex, zone).group()

        public_interface = information.get('networkInterfaces')[0]
        network = public_interface.get('accessConfigs')[0]

        creation_date = datetime.fromisoformat(
            information.get('creationTimestamp')
        )

        machine = DBMachine(
            execution=execution,
            name=information.get('name'),
            zone=zone,
            ip=network.get('natIP'),
            gcp_id=information.get('id'),
            status=MachineStatus.CREATED,
            creation_at=creation_date,
        )

        try:
            machine.save()
        except Exception:
            raise RuntimeError('Can not save information')

        return machine


class DeleteMachine:

    @classmethod
    def handle(cls, name: str, zone: str) -> bool:
        project = environ.get('GCP_PROJECT')
        command = f'gcloud compute instances delete {name} ' \
                  f'--project={project} ' \
                  f'--zone={zone} ' \
                  f'--quiet '\
                  f'--format=json'

        information, is_invalid = cls._run_command(command)
        if is_invalid:
            return True
        return False

    @classmethod
    def _run_command(cls, command: str) -> Tuple[Optional[dict], bool]:
        out = run(command.split(" "), stdout=PIPE, stderr=STDOUT)
        if out.returncode != 0:
            return None, True
        return {}, False
