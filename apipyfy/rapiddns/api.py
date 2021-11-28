import logging

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse as dt_parse

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-rapiddns')


class RapidDNSAPI(BaseAPI):
    """
    API for rapiddns.io

    Retrieve subdomains and reverse

    example:
        >>> api = RapidDNSAPI()
        >>> for d in api.subdomains('domain.tld'):
        >>>    print(d)
        {'domain': 'sub.domain.tld', 'target': '1.1.1.1', 'type': 'A', 'date': <datetime>}
        >>> for d in api.reverse_dns('1.1.1.1'):
        >>>    print(d)
        {'domain': 'domain.tld', 'target': '1.1.1.1', 'type': 'A', 'date': <datetime>}
    """
    def __init__(self, user_agent=None, proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'host': 'rapiddns.io' 
        })
        self._real_ip = '149.28.37.243'

    def subdomains(self, domain):
        results = []
        try:
            req = self.session.get(f'http://{self._real_ip}/s/{domain}', timeout=10)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            table = soup.find(id='table')
            for tr in table.findAll('tr'):
                tds = tr.findAll('td')
                if len(tds) == 0:
                    continue
                results.append({'domain': tds[0].text.strip(),
                                'target': tds[1].text.strip(),
                                'type': tds[2].text.strip(),
                                'date': dt_parse(tds[3].text.strip())})
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

    def reverse_dns(self, ip):
        results = []
        try:
            req = self.session.get(f'http://{self._real_ip}/sameip/{ip}')
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            table = soup.find(id='table')
            for tr in table.findAll('tr'):
                tds = tr.findAll('td')
                if len(tds) == 0:
                    continue
                results.append({'domain': tds[0].text.strip(),
                                'target': tds[1].text.strip(),
                                'type': tds[2].text.strip(),
                                'date': dt_parse(tds[3].text.strip())})
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