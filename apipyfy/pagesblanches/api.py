import logging
import re

import requests
from bs4 import BeautifulSoup

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-pagesblanches')

class PagesBlanchesAPI(BaseAPI):
    """
    API for https://www.118000.fr

    Retrieve Address and Phone for a given person

    example:
        >>> api = PagesBlanchesAPI()
        >>> for p in api.search('John Doe'):
        >>>    print(p)
        {'name': 'John Doe', 'address': '1 Avenue du Paradis 75000 Paris', 'phone': '0102030405'}
    """
    def __init__(self, user_agent=None, proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self._base_url = 'https://www.118000.fr/search'
    
    def search(self, full_name):
        results = []
        try:
            params = {'who': full_name}
            req = self.session.get(self._base_url, params=params, timeout=60)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            for section in soup.find_all('section', attrs={'class': 'card part'}):
                user = {'name': None, 'address': None, 'phone': None}
                # Name
                h2 = section.find('h2')
                if h2 is None:
                    continue
                user['name'] = h2.text.strip().title()
                # Address
                div = section.find('div', attrs={'class': 'h4 address mtreset'})
                if div is not None:
                    addr = []
                    for l in div.text.split('\n'):
                        addr.append(l.strip())
                    user['address'] = ' '.join(addr)
                # Phone
                p = section.find('p', attrs={'class': 'phone h2'})
                if p is not None:
                    user['phone'] = p.text.strip().replace(' ', '')
                results.append(user)
            return results
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
