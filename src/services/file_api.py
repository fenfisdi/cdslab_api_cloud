from os import environ
from typing import Tuple, Union
from uuid import UUID

from requests import Response

from src.utils.response import UJSONResponse, to_response
from .service import API, APIService


class FileAPI:
    api_url = environ.get('FILE_API')
    request = APIService(API(api_url))

    @classmethod
    def find_file(
        cls,
        simulation_id: Union[UUID, str],
        file_id: Union[UUID, str]
    ) -> Tuple[Union[Response, UJSONResponse], bool]:
        endpoint = f'/root/simulation/{str(simulation_id)}/file/{str(file_id)}'
        response = cls.request.get(endpoint)
        if not response.ok:
            return to_response(response), True
        return response, False
