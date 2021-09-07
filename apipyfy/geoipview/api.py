from apipyfy.base import BaseAPI
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger('apipyfy-geoipview')


class GeoIpViewAPI(BaseAPI):
    """
    API for geoipview.com

    Retrieve Geo Data

    example:
        >>> api = GeoIpViewAPI()
        >>> r= api.get_infos('1.1.1.1'):
        >>> print(r)
        {'lat': -37.700000762939, 'long': 145.18330383301, 'country_name': 'Australia', 'country_code': 'AU', 'city_name': 'Research'}
    """
    def __init__(self, user_agent='ApiPyFy/1.0.0', proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self._base_url = 'https://en.geoipview.com'

    def get_infos(self, ip):
        result = {'lat': None, 'long': None, 'country_name': None, 'country_code': None, 'city_name': None}
        try:
            req = self.session.get(self._base_url,
                                   params={'q': ip},
                                   timeout=5)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            soup_div = soup.find('div', attrs={'id': 'ipinfo_show'})
            if soup_div is None:
                logger.debug('Result div not found')
                return None

            for tr in soup_div.findAll('tr'):
                tds = tr.findAll('td')
                key = tds[0].text.strip()
                value = tds[1].text.strip()

                if key == 'Country Code:':
                    t = value.split('/')
                    if len(t) > 1:
                        result['country_code'] = t[1].strip()
                elif key == 'Country:':
                    result['country_name'] = value.strip()
                elif key == 'City:':
                    result['city_name'] = value.strip()
                elif key == 'Latitude:':
                    result['lat'] = float(value.strip())
                elif key == 'Longitude:':
                    result['long'] = float(value.strip())
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