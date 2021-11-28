import logging

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse as dt_parse

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-openbugbounty')


class OpenBugbountyAPI(BaseAPI):
    """
    API for openbugbounty.org

    Retrieve Vulns from Domain name

    example:
        >>> api = OpenBugbountyAPI()
        >>> r = api.search('facebook.com'):
        >>> print(r)
        {'id': 1162858, 'domain': 'facebook.com', 'researcher': 'DkilerS2', 'status': 'unpatched', 'type': 'Cross Site Scripting', 'date': datetime.datetime(2020, 5, 16, 0, 0)}
    """
    def __init__(self, user_agent=None, proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self._base_url = 'http://213.168.250.151'
        self.session.headers.update({'Host':'www.openbugbounty.org'})

    def search(self, domain):
        result = []
        try:
            payload = {'search': domain,
                       'researcher': None,
                       'program': None}
            req = self.session.get(f"{self._base_url}/search", params=payload, timeout=5)
            req.raise_for_status()
            # Check for refresh
            soup = BeautifulSoup(req.content, 'html.parser')
            table = soup.find('table', attrs={'class': 'search-results'})
            if table is None:
                logger.debug('Result table not found')
                return None
            for tr in table.findAll('tr'):
                tds = tr.findAll('td')
                if tds[0].text == 'Domain':
                    continue
                r = {'id': None, 'domain': None, 'researcher': None, 'status': None, 'type': None, 'date': None}
                r['domain'] = tds[0].text.strip()
                r['researcher'] = tds[1].text.split('\r')[0].strip()
                r['status'] = tds[3].text.strip()
                r['type'] = tds[4].text.strip()
                r['date'] = dt_parse(tds[2].text.strip())
                a = tds[0].find('a')
                id = a['href'].split('/')[-2]
                r['id'] = int(id)
                result.append(r)
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
