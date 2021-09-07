import logging

import requests
from bs4 import BeautifulSoup

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-domainmetrics')


class DomainmetricsAPI(BaseAPI):
    """
    API for domainmetrics.de

    Retrieve domain, google analytics ID and google adsense ID

    example:
        >>> api = DomainmetricsAPI()
        >>> t = api.search_domain('domain.tld'):
        >>>    print(t)
        {'google_analytics': ['UA-1111111'], 'google_adsense': ['pub-xxxxxxx']}
        >>> for d in api.search_google_analytics('UA-1111111'):
        >>>    print(d)
        domain.tld
        >>> for d in api.search_google_adsense('pub-xxxxxxx'):
        >>>    print(d)
        domain.tld      
    """
    def __init__(self, user_agent='ApiPyFy/1.0.0', proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self._base_url = 'http://www.domainmetrics.de'

    def search_domain(self, domain):
        result = {'google_analytics': set(), 'google_adsense': set()}
        try:
            req = self.session.get(f"{self._base_url}/domain/{domain}", 
                                 timeout=5)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            for a in soup.findAll('a'):
                if a.get('href').startswith('/analytics/'):
                    ga = a.text.strip()
                    ga = ga.split('-')
                    ga = '-'.join(ga[:2])
                    result['google_analytics'].add(ga)
                elif a.get('href').startswith('/adsense/'):
                    result['google_adsense'].add(a.text.strip())
            result['google_analytics'] = list(result['google_analytics'])
            result['google_adsense'] = list(result['google_adsense'])
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
 
    def search_google_analytics(self, ua):
        t = ua.split('-')
        if len(t) < 2:
            logger.error(f"Bad format, must match UA-XXXXXXXXX.")
            return None
        try:
        # On regarde tous les liens
            results = set()
            req = self.session.get(f"{self._base_url}/analytics/{t[1]}", 
                                   timeout=5)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            for a in soup.findAll('a'):

                if a.get('href').startswith('/domain/'):
                    results.add(a.text.strip())
            return list(results)
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

    def search_google_adsense(self, pub):
        t = pub.split('-')
        if len(t) < 2:
            logger.error(f"Bad format, must match pub-xxxxxxxxxxxxxxxx.")
            return None
        try:
            results = set()
            req = self.session.get(f"{self._base_url}/adsense/{t[1]}", 
                                 verify=False, timeout=5)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            for a in soup.findAll('a'):
                if a.get('href').startswith('/domain/'):
                    results.add(a.text.strip())
            return list(results)
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
