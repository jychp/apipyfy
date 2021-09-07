import logging
import re

import requests
from bs4 import BeautifulSoup

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-moonsearch')


class MoonsearchAPI(BaseAPI):
    ANALYTICS_REGEX = re.compile(r'Google Analytics ([0-9]+)')
    SENSE_REGEX = re.compile(r'Google AdSense ([0-9]+)')
    """
    API for moonsearch.com

    Retrieve domain, google analytics ID and google adsense ID

    example:
        >>> api = MoonsearchAPI()
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
        self._base_url = 'https://moonsearch.com'

    def search_domain(self, domain):
        result = {'google_analytics': [], 'google_adsense': []}
        try:
            req = self.session.get(f"{self._base_url}/report/{domain}.html)", 
                                 verify=False, timeout=5)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            # On cherche le analytics
            analytics_sec = soup.find('section', attrs={'id': 'analytics'})
            if analytics_sec is not None:
                for ua in self.ANALYTICS_REGEX.findall(analytics_sec.text):
                    result['google_analytics'].append('UA-{0}'.format(ua))
            # On cherche le pubid
            sense_sec = soup.find('section', attrs={'id': 'sense'})
            if sense_sec is not None:
                for s in self.SENSE_REGEX.findall(sense_sec.text):
                    result['google_adsense'].append('pub-{0}'.format(s))
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
        results = set()
        t = ua.split('-')
        if len(t) < 2:
            logger.error(f"Bad format, must match UA-XXXXXXXXX.")
            return None
        try:
            req = self.session.get(f"{self._base_url}/analytics/{t[1]}.html", 
                                 verify=False, timeout=5)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            for a in soup.findAll('a'):
                if a.get('href').startswith('/report/') and a.get('target') == '_blank':
                    domain = a.text.strip()
                    break
            if domain is None:
                return []
            p = 1
            while True:
                payload = {'d': domain,
                        'ps': 100,
                        't': 0,
                        'sf': 0,
                        'so': 0,
                        'p': p}
                req = self.session.get(f"{self._base_url}/page", params=payload, timeout=5, verify=False)
                req.raise_for_status()
                try:
                    for i in req.json():
                        results.add(i)
                    p += 1
                except Exception:
                    break
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
        results = set()
        if len(t) < 2:
            logger.error(f"Bad format, must match pub-xxxxxxxxxxxxxxxx.")
            return None
        try:
            req = self.session.get(f"{self._base_url}/adsense/{t[1]}.html", 
                                 verify=False, timeout=5)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            for a in soup.findAll('a'):
                if a.get('href').startswith('/report/') and a.get('target') == '_blank':
                    domain = a.text.strip()
                    break
            if domain is None:
                return []
            p = 1
            while True:
                payload = {'d': domain,
                        'ps': 100,
                        't': 0,
                        'sf': 0,
                        'so': 0,
                        'p': p}
                req = self.session.get(f"{self._base_url}/page", params=payload, timeout=5, verify=False)
                req.raise_for_status()
                try:
                    for i in req.json():
                        results.add(i)
                    p += 1
                except Exception:
                    break
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
