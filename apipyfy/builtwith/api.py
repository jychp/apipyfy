import logging

import requests
from bs4 import BeautifulSoup

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-builtwith')


class BuiltWithAPI(BaseAPI):
    """
    API for builtwith.com

    Retrieve web site info (CMS, Serveur type etc ...)

    example:
        >>> api = BuiltWithAPI()
        >>> for d in api.info('domain.tld'):
        >>>    print(d)
        {'Category': ['element1', 'element2']}
    """
    def __init__(self, user_agent='ApiPyFy/1.0.0', proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self._base_url = 'https://builtwith.com'

    def info(self, domain):
        result = {}
        try:
            req = self.session.get(f"{self._base_url}/{domain}", timeout=5)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            rows = soup.findAll('div', attrs={'class': 'card-body pb-0'})
            for row in rows:
                title = row.find('h6')
                names = row.findAll('h2')
                if title is None:
                    continue
                title = title.text
                result[title] = []
                for name in names:
                    name = name.text
                    if name == title:
                        continue
                    result[title].append(name)
            return result
        except requests.exceptions.HTTPError as errh:
            logger.error(f"Http Error: {errh}")
            return None
        except requests.exceptions.ConnectionError as errc:
            logger.error(f"Error Connecting: {errc}")
            return None
        except requests.exceptions.Timeout as errt:
            logger.error(f"Timeout Error: {errt}")
            return None
        except requests.exceptions.RequestException as err:
            logger.error(f"Uh-oh: Something Bad Happened {err}")
            return None
        
