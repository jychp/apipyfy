import logging

import requests
from bs4 import BeautifulSoup

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-reversewhois')


class ReverseWhoisAPI(BaseAPI):
    """
    API for reversewhois.io

    Retrieve Domains from Registrant Name or Email

    example:
        >>> api = ReverseWhoisAPI()
        >>> for d in api.search('domain@fb.com'):
        >>> print(d)
        facebook.com
    """
    def __init__(self, user_agent=None, proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self._base_url = 'https://www.reversewhois.io'

    def search(self, q):
        result = []
        try:
            req = self.session.get(self._base_url,
                                   params={'searchterm': q},
                                   timeout=5)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            for tr in soup.findAll('tr'):
                tds = tr.findAll('td')
                if len(tds) != 4:
                    continue
                if not tds[0].text.isnumeric():
                    continue
                result.append(tds[1].text.strip())
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
