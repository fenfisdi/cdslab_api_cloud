from os import environ
from typing import Tuple, Union
from uuid import UUID

from requests import Response

from src.utils.response import UJSONResponse, to_response
from .service import API, APIService


class ConfigAPI:
    api_url = environ.get('CONFIG_API')
    request = APIService(API(api_url))

    @classmethod
    def update_configuration_status(
        cls,
        simulation_id: Union[UUID, str],
        status: str
    ) -> Tuple[Union[Response, UJSONResponse], bool]:
        parameters = {
            "status": status,
        }
        endpoint = f'/root/simulation/{str(simulation_id)}/finish'
        response = cls.request.get(endpoint, parameters=parameters)
        if not response.ok:
            return to_response(response), True
        return response, False
