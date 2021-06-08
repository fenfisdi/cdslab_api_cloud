from dataclasses import dataclass


@dataclass
class SecurityMessage:
    without_privileges: str = 'User without privileges'
    invalid_token: str = 'Invalid Token'


@dataclass
class GoogleMessage:
    created: str = 'Simulation Instance Created'
    error: str = 'Can not create GCP Instance'
    not_session: str = 'Can not start Session'
