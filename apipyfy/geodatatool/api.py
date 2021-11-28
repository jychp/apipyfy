from apipyfy.base import BaseAPI
import logging
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger('apipyfy-geodatatool')


class GeodataToolAPI(BaseAPI):
    """
    API for geodatatool.com

    Retrieve Geo Data

    example:
        >>> api = GeodataToolAPI()
        >>> r= api.get_infos('1.1.1.1'):
        >>> print(r)
        {'lat': 34.05223, 'long': -118.24368, 'country_name': 'United States', 'country_code': 'US', 'city_name': None}
    """
    def __init__(self, user_agent=None, proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self._base_url = 'https://www.geodatatool.com/en/'

    def get_infos(self, ip):
        result = {'lat': None, 'long': None, 'country_name': None, 'country_code': None, 'city_name': None}
        try:
            req = self.session.get(self._base_url,
                                   params={'ip': ip},
                                   timeout=5)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            for div in soup.findAll('div', attrs={'class': 'data-item'}):
                first_span = True
                spantype = None
                for span in div.findAll('span'):
                    if first_span:
                        spantype = span.text.strip()
                    first_span = False
                else:
                    spanvalue = span.text.strip()
                    if spantype == 'City':
                        result['city_name'] = spanvalue
                    elif spantype == 'Latitude:':
                        result['lat'] = float(spanvalue)
                    elif spantype == 'Longitude:':
                        result['long'] = float(spanvalue)
                    elif spantype == 'Country Code:':
                        result['country_code'] = spanvalue.replace(' ()', '')
                    elif spantype == 'Country:':
                        result['country_name'] = spanvalue

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
