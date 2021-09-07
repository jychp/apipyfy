from abc import ABC

import requests


class BaseAPI(ABC):
    """ Base class for every API """
    def __init__(self, user_agent='ApiPyFy/1.0.0', proxy=None) -> None:
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': user_agent})
        self.session.proxies.update({'http': proxy, 'https': proxy})
