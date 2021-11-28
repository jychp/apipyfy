import re
import logging

import requests
from bs4 import BeautifulSoup

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-dnsdumpster')


class DNSDumpsterAPI(BaseAPI):
    REGEX_IP = re.compile(r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})')
    """
    API for dnsdumpster.com

    Retrieve subdomains

    example:
        >>> api = DNSDumpsterAPI()
        >>> for d in api.subdomains('domain.tld'):
        >>>    print(d)
        {'domain': 'sub.domain.tld', 'target': '1.1.1.1', 'type': 'A', 'date': None}
    """
    def __init__(self, user_agent=None, proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self._base_url = 'https://dnsdumpster.com/'
        self.session.headers.update({'Referer': self._base_url})

    def _retrieve_results(self, search_domain, table, record_type):
        res = []
        trs = table.findAll('tr')
        for tr in trs:
            tds = tr.findAll('td')
            ip = self.REGEX_IP.findall(tds[1].text)[0]
            domain = str(tds[0]).split('<br/>')[0].split('>')[1]
            if domain == search_domain:
                continue
            res.append({'domain': domain, 'target': ip, 'type': record_type, 'date': None})
        return res

    def subdomains(self, domain) -> list:
        result = []
        # Get CSRF Token
        try:
            req = self.session.get(self._base_url, timeout=5)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            csrf_middleware_list = soup.findAll('input', attrs={'name': 'csrfmiddlewaretoken'})
            if len(csrf_middleware_list) == 0:
                logging.debug('Can not find CSRF Token.')
                return None
            csrf_middleware = csrf_middleware_list[0].get('value', None)
            if csrf_middleware is None:
                logging.debug('Empty CSRF token')
                return None
            cookies = {'csrftoken': csrf_middleware}
            data = {'csrfmiddlewaretoken': csrf_middleware, 'targetip': domain, 'user': 'free'}
            # Send form
            req = self.session.post(self._base_url, cookies=cookies, data=data, timeout=5)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            tables = soup.findAll('table')

            if len(tables) > 0:
                result += self._retrieve_results(domain, tables[0], 'ns')
            if len(tables) > 1:
                result += self._retrieve_results(domain, tables[1], 'mx')
            if len(tables) > 3:
                result += self._retrieve_results(domain, tables[3], 'a')

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