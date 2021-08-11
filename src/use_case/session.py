from base64 import b64decode
from os import environ, path
from subprocess import PIPE, STDOUT, run
from tempfile import NamedTemporaryFile


class SessionUseCase:
    service_account = environ.get('GCP_SERVICE_ACCOUNT')
    gcp_key = environ.get('GCP_KEY')

    @classmethod
    async def create_session(cls) -> bool:
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
        return False
