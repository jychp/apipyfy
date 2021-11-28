import time
import logging

import requests
from bs4 import BeautifulSoup

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-w3techs')


class W3TechsAPI(BaseAPI):
    """
    API for w3techs.com

    Retrieve CMS and website infos from domain

    example:
        >>> api = ReverseWhoisAPI()
        >>> r = api.info('facebook.com'):
        >>> print(r)
        {'Server-side Programming Language': ['PHP'], 'Client-side Programming Language': ['JavaScript'], 'SSL Certificate Authority': ['DigiCert'], 'Advertising Networks': ['Google Ads', 'Microsoft Advertising'], 'Site Elements': ['External CSS', 'Embedded CSS', 'Inline CSS', 'Cookies expiring in months', 'Cookies expiring in years', 'HttpOnly Cookies', 'Secure Cookies', 'Brotli Compression', 'IPv6', 'HTTP/3', 'HTTP Strict Transport Security', 'Default subdomain www', 'Default protocol https', 'Session Cookies', 'Non-Secure Cookies'], 'Structured Data Formats': ['Open Graph', 'JSON-LD'], 'Markup Language': ['HTML5'], 'Character Encoding': ['UTF-8'], 'Image File Formats': ['SVG', 'GIF', 'PNG'], 'Top Level Domain': ['.com'], 'Server Locations': ['United States'], 'Content Languages': ['English'], 'Share this page': []}
    """
    def __init__(self, user_agent=None, proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self._base_url = 'https://w3techs.com/sites/info'

    def info(self, domain):
        result = {}
        try:
            req = self.session.get(f"{self._base_url}/{domain}", timeout=5)
            req.raise_for_status()
            # Check for refresh
            soup = BeautifulSoup(req.content, 'html.parser')
            refresh = soup.find('input', attrs={'name': 'add_site'})
            if refresh is not None:
                logger.info('Ask for refresh, wait 5 sec')
                payload = {'add_site':'+Crawl+now!+'}
                req = requests.post(f"{self._base_url}/{domain}", timeout=5, data=payload)
                req.raise_for_status()
                time.sleep(5)
                req = self.session.get(f"{self._base_url}/{domain}", timeout=5)
                req.raise_for_status()
            # Parse
            soup = BeautifulSoup(req.content, 'html.parser')
            main_td = soup.find('td', attrs={'class': 'tech_main'})
            last_h = None
            for p in main_td.findAll('p'):
                if not p.get('class'):
                    continue
                if p['class'][0] == 'si_h':
                    h = p.text.split('<')[0].strip()
                    if len(h) > 50:
                        continue
                    result[h] = []
                    last_h = h
                elif last_h is None:
                    continue
                else:
                    a = p.find('a')
                    result[last_h].append(a.text.strip())
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
