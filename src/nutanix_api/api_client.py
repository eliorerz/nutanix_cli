import warnings
from abc import abstractmethod, ABC
from http import HTTPStatus
from typing import Union, Dict, Any, Callable

import requests
from requests import Session
from urllib3.exceptions import InsecureRequestWarning, RequestError


class ApiObject(ABC):

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        pass


class NutanixSession:
    HEADERS = {"Content-Type": "application/json", "charset": "utf-8"}

    def __init__(self, username: str, password: str, insecure: bool = True):
        session = requests.Session()
        session.auth = (username, password)
        session.verify = False
        session.headers.update({'Content-Type': 'application/json; charset=utf-8'})
        self._session = session
        self._insecure = insecure

    def __enter__(self) -> Session:
        if self._insecure:
            warnings.simplefilter("ignore", InsecureRequestWarning)
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._insecure:
            warnings.simplefilter("default", InsecureRequestWarning)

        self._session.close()
        return self


class NutanixApiClient:
    URL_FORMAT = "https://{address}:{port}/api/nutanix/v3/"

    def __init__(self, username: str, password: str, port: Union[str, int], address: str):
        self._username = username
        self._password = password
        self._port = int(port)
        self._url = self.URL_FORMAT.format(address=address, port=port)

    @classmethod
    def _request(cls, url: str, method: Callable, body: Dict[str, Any] = None):
        server_response = method(url) if body is None else method(url, json=body)
        if server_response.status_code != HTTPStatus.OK and server_response.status_code != HTTPStatus.ACCEPTED:
            raise RequestError(server_response.json())

        return server_response.json()

    def GET(self, relative_url: str) -> Union[Dict[str, Any], None]:  # noqa
        with NutanixSession(self._username, self._password) as session:
            return self._request(self._url + relative_url, session.get)

    def POST(self, relative_url: str, body: Dict[str, Any] = None) -> Union[Dict[str, Any], None]:  # noqa
        with NutanixSession(self._username, self._password) as session:
            return self._request(self._url + relative_url, session.post, body or {})

    def PUT(self, relative_url: str, body: Dict[str, Any] = None) -> Union[Dict[str, Any], None]:  # noqa
        with NutanixSession(self._username, self._password) as session:
            return self._request(self._url + relative_url, session.put, body or {})
