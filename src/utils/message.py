from dataclasses import dataclass


@dataclass
class SecurityMessage:
    without_privileges: str = 'User without privileges'
    invalid_token: str = 'Invalid Token'


@dataclass
class MachineMessage:
    deleted: str = 'Machine will delete soon'
    exist: str = 'Machine exist'
    created: str = 'Machine has been created'
    not_found: str = 'Machine not found'


@dataclass
class GoogleMessage:
    unavailable: str = 'Google session unavailable'
    created: str = 'Simulation Instance Created'
    error: str = 'Can not create GCP Instance'
    not_session: str = 'Can not start Session'
