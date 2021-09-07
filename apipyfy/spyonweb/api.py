import logging
import re

import requests
from bs4 import BeautifulSoup

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-spyonweb')


class SpyOnWebAPI(BaseAPI):
    REGEX_PUB = re.compile(f'pub-[\d]+')
    REGEX_UA = re.compile(f'UA-[a-zA-Z\d]+')
    """
    API for spyonweb.com

    Retrieve domain, google analytics ID and google adsense ID

    example:
        >>> api = SpyOnWebAPI()
        >>> t = api.search_domain('domain.tld'):
        >>>    print(t)
        {'google_analytics': ['UA-1111111'], 'google_adsense': ['pub-xxxxxxx']}
        >>> for d in api.search_google_analytics('UA-1111111'):
        >>>    print(d)
        domain.tld
        >>> for d in api.search_google_adsense('pub-xxxxxxx'):
        >>>    print(d)
        domain.tld
        >>> for d in api.reverse_dns('1.1.1.1'):
        >>>    print(d)
        domain.tld 
    """
    def __init__(self, user_agent='ApiPyFy/1.0.0', proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self._base_url = 'https://spyonweb.com'

    def search_domain(self, domain):
        result = {'google_analytics': set(), 'google_adsense': set()}
        try:
            req = self.session.get(f"{self._base_url}/{domain}", timeout=5)
            req.raise_for_status()
            for ua in self.REGEX_UA.findall(req.text):
                if ua in ('UA-xxxxxxx', 'UA-Compatible', 'UA-8064537'):
                    continue
                result['google_analytics'].add(ua)
            for pub in self.REGEX_PUB.findall(req.text):
                result['google_adsense'].add(pub)
            result['google_adsense'] = list(result['google_adsense'])
            result['google_analytics'] = list(result['google_analytics'])
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

    def _search(self, item):
        try:
            results = set()
            req = self.session.get(f"{self._base_url}/{item}", timeout=5)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            for div in soup.findAll('div', attrs={'class': 'links'}):
                for a in div.findAll('a'):
                    d = a.text.strip()
                    if len(d) == 0:
                        continue
                    results.add(d)
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

    def search_google_analytics(self, ua):
        t = ua.split('-')
        if len(t) < 2:
            logger.error(f"Bad format, must match UA-XXXXXXXXX.")
            return None
        return self._search(ua)


    def search_google_adsense(self, pub):
        t = pub.split('-')
        if len(t) < 2:
            logger.error(f"Bad format, must match pub-xxxxxxxxxxxxxxxx.")
            return None
        return self._search(pub)

    def reverse_dns(self, ip):
        return self._search(ip)
