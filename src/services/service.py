from dataclasses import dataclass

from requests import Request, Session
from requests.models import Response


@dataclass
class API:
    url: str


class APIService:

    def __init__(self, api: API):
        self.api = api
        self.session = Session()

    def __url(self, endpoint: str) -> str:
        return "".join([self.api.url, endpoint])

    def post(
        self,
        endpoint: str,
        data: dict = None,
        parameters: dict = None
    ) -> Response:
        request = Request(
            url=self.__url(endpoint),
            method='POST',
            params=parameters,
            json=data

        ).prepare()
        return self.session.send(request)

    def put(
        self,
        endpoint: str,
        data: dict = None,
        parameters: dict = None
    ) -> Response:
        request = Request(
            url=self.__url(endpoint),
            method='PUT',
            params=parameters,
            json=data
        ).prepare()
        return self.session.send(request)

    def get(self, endpoint: str, parameters: dict = None) -> Response:
        request = Request(
            url=self.__url(endpoint),
            method='GET',
            params=parameters
        ).prepare()
        return self.session.send(request)
