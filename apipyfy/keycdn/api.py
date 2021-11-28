import logging
import urllib3

import requests
from bs4 import BeautifulSoup

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-keycdn')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class KeyCDNAPI(BaseAPI):
    """
    API for keycdn.com

    Retrieve Geo Data

    example:
        >>> api = KeyCDNAPI()
        >>> r= api.get_infos('1.1.1.1'):
        >>> print(r)
        {'lat': -33.494, 'long': 143.2104, 'country_name': 'Australia', 'country_code': 'au', 'city_name': None, 'asn': 13335, 'provider': 'CLOUDFLARENET'}
    """
    def __init__(self, user_agent=None, proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self.session.headers.update({'Accept': 'application/json, text/javascript, */*; q=0.01',
                                     'X-Requested-With': 'XMLHttpRequest'})
        self._base_url = 'https://tools.keycdn.com/geo'

    def get_infos(self, ip):
        result = {'lat': None, 'long': None, 'country_name': None, 'country_code': None, 'city_name': None, 'asn': None, 'provider': None}
        try:
            req = self.session.get(self._base_url,
                                   params={'host': ip},
                                   verify=False,
                                   timeout=5)
            req.raise_for_status()
            data = {}
            soup = BeautifulSoup(req.content, 'html.parser')
            div = soup.find(id='geoResult')
            dts = div.findAll('dt')
            dds = div.findAll('dd')
            for dt, dd in zip(dts, dds):
                data[dt.text] = dd.text
            if data.get('City') is not None:
                result['city_name'] = data.get('City')
            if data.get('Country') is not None:
                country_name, s = data.get('Country').split('(')
                result['country_name'] = country_name.strip()
                result['country_code'] = s.split(')')[0].lower()
            if data.get('Coordinates') is not None:
                lat, s, _ = data.get('Coordinates').split('(')
                lon = s.split('/')[-1]
                result['lat'] = float(lat.strip())
                result['long'] = float(lon.strip())
            if data.get('ASN') is not None:
                result['asn'] = int(data.get('ASN'))
            result['provider'] = data.get('Provider')
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
