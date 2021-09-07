import base64
import logging

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse as dt_parse

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-fofa')


class FofaAPI(BaseAPI):
    """
    API for fofa.so

    Search on scan DB

    example:
        >>> api = FofaAPI()
        >>> for d in api.search('"Sailor 900"'):
        >>>    print(d)
    """
    def __init__(self, user_agent='ApiPyFy/1.0.0', proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self._base_url = 'https://fofa.so'

    def search(self, query):
        results = []
        payload = {'qbase64': base64.b64encode(query.encode()).decode('utf-8')}
        try:
            req = self.session.get(f"{self._base_url}/result", params=payload, timeout=15)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            for div in soup.findAll('div', attrs={'class': 'rightListsMain'}):
                result = {
                    "title": None,
                    "ip": None,
                    'port': None,
                    'asn': None,
                    'organization': None,
                    'hostname': None,
                    'last_seen': None,
                    'softwares': [],
                    'body': None,
                    'certificate': None,
                }
                header = div.find('div', attrs={'class': 'listAddr'})
                if header is None:
                    continue
                port = header.find('a', attrs={'class': 'portHover'})
                result['port'] = int(port.text)
                content = div.find('div', attrs={'class': 'contentMain'})
                if content is None:
                    continue
                content_left = content.find('div', attrs={'class': 'contentLeft'})
                content_right = content.find('div', attrs={'class': 'contentRight'})
                # Left data
                step = None
                for p in content_left.findAll('p'):
                    if step is None:
                        a = p.find('a')
                        if a is None:
                            result['title'] = p.text
                        else:
                            result['ip'] = a.text
                            step = 'ip'
                    elif step == 'ip':
                        a = p.find('a')
                        result['asn'] = a.text
                        step = 'asn'
                    elif step == 'asn':
                        a = p.find('a')
                        result['organization'] = a.text
                        step = 'org'
                    elif step == 'org':
                        a = p.find('a')
                        if a is not None:
                            result['hostname'] = p.text
                        else:
                            result['last_seen'] = dt_parse(p.text)
                            step = 'last_seen'
                    else:
                        try:
                            if 'listSpanCont' in p.attrs['class']:
                                for a in p.findAll('a'):
                                    result['softwares'].append(a.text)
                        except KeyError as e:
                            pass
                # Right data
                body_div = content_right.find('div', attrs={'class': 'bodyContent'})
                result['body'] = body_div.find('span').text
                certificate_div = content_right.find('div', attrs={'class': 'certs-detail'})
                if certificate_div is not None:
                    result['certificate'] = certificate_div.text
                results.append(result)

            return results

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
