from multiprocessing import Manager
import time

from .zoomeyejs import ZoomEyeJs

from apipyfy.base import BaseAPI
import requests

import logging

logger = logging.getLogger('apipyfy-zoomeye')


class ZoomEyeAPI(BaseAPI):
    """
    API for zoomeye.org

    Search on scan DB

    example:
        >>> api = ZoomEye()
        >>> for d in api.search('"Sailor 900"'):
        >>>    print(d)
    """
    def __init__(self, user_agent=None, proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self._base_url = 'https://www.zoomeye.org'
        self.session.headers.update({'Host': 'www.zoomeye.org',
                                     'Referer': 'https://www.zoomeye.org/',
                                     'Cache-Control': 'no-cache',
                                     'Connection': 'keep-alive',
                                     'Pragma':'no-cache',
                                     'Upgrade-Insecure-Requests': '1',
                                     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                                     'Accept-Language': 'en-US;q=0.5,en;q=0.3'})

    def _bypass(self, content, retry=2):
        # Get __cdnuid
        try:
            token = self._get_token(content)
            logger.info(f'Token: {token}')
            self.session.cookies.set('__cdn_clearance', token, path='/', domain='www.zoomeye.org')
            time.sleep(2)
            req_cookie = self.session.get(self._base_url, timeout=5)
            if req_cookie.status_code == 521:
                if retry > 1:
                    return self._init_cookie(retry=retry - 1)
                return False
            if req_cookie.status_code == 200:
                return True
            else:
                return False
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

    def _get_token(self, raw_script):
        manager = Manager()
        result = manager.list()
        js = ZoomEyeJs(raw_script, result)
        js.start()
        start_time = time.time()
        while len(js.result) == 0:
            delta = time.time() - start_time
            if delta >= 5:
                break
            if not js.is_alive():
                break
            time.sleep(1)
        # Kill
        if js.is_alive():
            js.terminate()
        # Get results
        if len(js.result) == 0:
            return None
        else:
            return js.result[0]

    def search(self, query, page=1, pageSize=20):
        payload = {'q': query,
                   'page': page,
                   'pageSize': pageSize}
        try:
            req_search = self.session.get(f"{self._base_url}/search", params=payload, timeout=30)
            if req_search.status_code == 521:
                if not self._bypass(req_search.text):
                    logger.error('Could not bypass anti-bot security.')
                    return None
                else:
                    req_search = self.session.get(f"{self._base_url}/search", params=payload, timeout=30)
                    if req_search.status_code != 200:
                        logger.error('Security bypass failed.')
                        return None
            return req_search.json()['matches']
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
