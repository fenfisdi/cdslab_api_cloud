from dataclasses import dataclass


@dataclass
class SecurityMessage:
    without_privileges: str = 'User without privileges'
    invalid_token: str = 'Invalid Token'
