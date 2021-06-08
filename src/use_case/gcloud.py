import re
from base64 import b64decode
from datetime import datetime
from json import loads
from os import environ, path
from subprocess import PIPE, STDOUT, run
from tempfile import NamedTemporaryFile
from typing import Optional, Tuple

from src.models.db import Machine, User


class SessionUseCase:
    service_account = environ.get('GCP_SERVICE_ACCOUNT')
    gcp_key = environ.get('GCP_KEY')

    @classmethod
    def create_session(cls) -> bool:
        gcp_key = environ.get('GCP_KEY')
        assert gcp_key, ValueError('GCP_KEY must be set')
        assert cls.service_account, ValueError(
            'GCP_SERVICE_ACCOUNT must be set'
        )

        access_key = b64decode(gcp_key)
        with NamedTemporaryFile(
                suffix='.json',
                prefix=path.basename(__file__)
        ) as file:
            file.write(access_key)
            file.flush()

            command = f'gcloud auth ' \
                      f'activate-service-account {cls.service_account} ' \
                      f'--key-file {file.name} ' \
                      f'--verbosity error ' \
                      f'--format json'

            out = run(command.split(" "), stdout=PIPE, stderr=STDOUT)

            if out.returncode != 0:
                raise RuntimeError(out.stdout.decode())

            return True


class MachineUseCase:
    service_account = environ.get('GCP_SERVICE_ACCOUNT')
    container = environ.get('GCP_CONTAINER')

    @classmethod
    def create(cls) -> Tuple[Optional[dict], bool]:
        scopes = [
            'https://www.googleapis.com/auth/devstorage.read_only',
            'https://www.googleapis.com/auth/logging.write',
            'https://www.googleapis.com/auth/monitoring.write',
            'https://www.googleapis.com/auth/servicecontrol',
            'https://www.googleapis.com/auth/service.management.readonly',
            'https://www.googleapis.com/auth/trace.append'
        ]
        name = "pastor-prueba-1"

        command = f'gcloud compute instances ' \
                  f'create-with-container {name} ' \
                  f'--project=poc-cdslib ' \
                  f'--zone=us-east1-c ' \
                  f'--machine-type=n2-custom-2-1024 ' \
                  f'--subnet=default ' \
                  f'--network-tier=PREMIUM ' \
                  f'--metadata=google-logging-enabled=true ' \
                  f'--maintenance-policy=TERMINATE ' \
                  f'--service-account={cls.service_account} ' \
                  f'--scopes {",".join(scopes)} ' \
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
                  f'--container-image=gcr.io/poc-cdslib/nginx:alpine'

        out = run(command.split(" "), stdout=PIPE, stderr=STDOUT)
        if out.returncode != 0:
            return None, True
        return cls._decode_success_message(out.stdout), False

    @classmethod
    def _decode_success_message(cls, message: bytes) -> dict:
        split_message = message.split(b'\n')
        json_message = b"\n".join(split_message[1:])
        try:
            return loads(json_message.decode('utf-8'))[0]
        except Exception as error:
            raise Exception(error)

    @classmethod
    def save(cls, information: dict, user: User) -> Machine:
        # Get Zone Instance
        zone_regex = r"(us-[a-z1-9A-Z]{3,8}-.$)"
        zone = information.get('zone')
        zone = re.search(zone_regex, zone).group()

        # Get Public IP
        public_interface = information.get('networkInterfaces')[0]
        network = public_interface.get('accessConfigs')[0]

        # Creation Date

        return Machine(
            user=user,
            name=information.get('name'),
            zone=zone,
            ip=network.get('natIP'),
            gcp_id=information.get('id'),
            creation_at=datetime.fromisoformat(
                information.get('creationTimestamp')
            )
        )
