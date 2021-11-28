import re
import urllib3
import logging

import requests

from apipyfy.base import BaseAPI

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
logger = logging.getLogger('apipyfy-dbip')


class DbIpAPI(BaseAPI):
    """
    API for db-ip.com

    Retrieve Geo Data and Blacklist

    example:
        >>> api = DbIpAPI()
        >>> r= api.get_infos('1.1.1.1'):
        >>> print(r)
        {'lat': -20.5, 'long': 120.15, 'country_code': 'au', 'city_name': 'Marble Bar', 'is_proxy': False, 'is_crawler': False, 'is_threat': False}
    """
    def __init__(self, user_agent=None, proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self.session.headers.update({'Host': 'db-ip.com'})
        self._base_url = 'https://144.217.254.112'

    def get_infos(self, ip):
        result = {'lat': None,
                  'long': None,
                  'country_code': None,
                  'city_name': None,
                  'is_proxy': False,
                  'is_crawler': False,
                  'is_threat': False}
        try:
            req = self.session.get(f"{self._base_url}/{ip}",
                                verify=False,
                                timeout=5)
            req.raise_for_status()
            # Search lat
            lats = re.findall(r"\"latitude\": \"([\d.-]+)\"", req.text)
            result['lat'] = float(lats[0])
            # Search long
            longs = re.findall(r"\"longitude\": \"([\d.-]+)\"", req.text)
            result['long'] = float(longs[0])
            # Search country
            countrys = re.findall(r"\"addressCountry\": \"(\w+)\"", req.text)
            if len(countrys) > 0:
                result['country_code'] = countrys[0].lower()
            # Search city
            citys = re.findall(r"\"city\": \"(.*)\"", req.text)
            if len(citys) > 0:
                result['city_name'] = citys[0]
            
            #  Search proxy
            if "<i class='fa fa-exclamation-triangle fa-4x text-warning' " \
            "title='This IP address is used by a proxy, vpn or Tor exit node'></i>" in req.text:
                result['is_proxy'] = True
            # Search crawler
            if "<i class='fa fa-check fa-4x text-success' " \
            "title='This IP address is used by a web crawler'></i>" in req.text:
                result['is_crawler'] = True
            # On regarde le cyber threat
            if "<i class='fa fa-exclamation-triangle fa-4x text-danger' " \
            "title='This IP address is a known source of cyber attack'></i>" in req.text:
                result['is_threat'] = True

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
