import logging

import requests
from bs4 import BeautifulSoup

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-ipfingerprints')


class IpFingerprintsAPI(BaseAPI):
    """
    API for ipfingerprints.com

    Retrieve Geo Data

    example:
        >>> api = IpFingerprintsAPI()
        >>> r= api.get_infos('1.1.1.1'):
        >>> print(r)
        {'lat': -33.493999, 'long': 143.210403, 'country_name': 'Australia', 'country_code': 'AU', 'city_name': None, 'provider': 'Mountain View Communications'}
    """
    def __init__(self, user_agent=None, proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self._base_url = 'https://www.ipfingerprints.com/scripts/getIPInfo.php'

    def get_infos(self, ip):
        result = {'lat': None, 'long': None, 'country_name': None, 'country_code': None, 'city_name': None, 'provider': None}
        try:
            req = self.session.post(self._base_url,
                                   data={'ip': ip},
                                   timeout=5)
            req.raise_for_status()
            soup = BeautifulSoup(req.json()['ipInfo'], 'html.parser')

            tdtype = None
            tdvalue = None
            for td in soup.findAll('td'):
                if td.get('class'):
                    if "small-head" in td['class'][0]:
                        tdtype = td.text.strip()
                    elif "small-desc" in td['class'][0] or "small-last" in td['class'][0]:
                        tdvalue = td.text.strip()
                    if tdtype and tdvalue:
                        if tdtype == 'Country':
                            name, code = tdvalue.split('(')
                            result['country_code'] = code[0:2].upper()
                            result['country_name'] = name.strip()
                        elif tdtype == 'City':
                            result['city_name'] = tdvalue
                        elif tdtype == 'Latitude':
                            result['lat'] = float(tdvalue)
                        elif tdtype == 'Longitude':
                            result['long'] = float(tdvalue)
                        elif tdtype == 'ISP':
                            result['provider'] = tdvalue
                        tdtype = None
                        tdvalue = None
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
