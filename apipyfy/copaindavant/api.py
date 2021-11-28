import logging

import requests
from bs4 import BeautifulSoup

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-copaindavant')


class CopainDavantAPI(BaseAPI):
    """
    API for https://copainsdavant.linternaute.com/

    Retrieve Personnal info and relationships

    example:
        >>> api = CopainDavantAPI()
        >>> for p in api.search('John Doe'):
        >>>    print(p)
        {'fullname': 'John Doe', 'id': 'john-doe-12345', 'avatar': 'https://image-uniservice.linternaute.com/image/75/5/12345/7890.jpg', 'birthday': '1 avril 1987', 'address': '1 avenue de Paradis Paris France', 'job': 'Pentester', 'rels': [{'id': 'alice-bob-22222', 'fullname': 'Alice Bob'}]}
    """
    def __init__(self, user_agent='ApiPyFy/1.0.0', proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self.session.headers.update({'Accept':'application/json, text/javascript, */*; q=0.01',
                                     'X-Requested-With':'XMLHttpRequest'})
        self._base_url = 'http://copainsdavant.linternaute.com'

    def search(self, full_name):
        try:
            results = []
            # Main requests
            params = {'full': '',
                      'q': full_name,
                      'ty': 1,
                      'xhr': 1}
            req = self.session.get(self._base_url + '/s/', params=params, timeout=60)
            req.raise_for_status()
            try:
                data = req.json()['$data']['copains']['users']
            except KeyError:
                return None
            # Parsing
            for uid, details in data.items():
                if uid == '0':
                    continue
                address = []
                if details.get('rue') is not None:
                    address.append(details['rue'])
                if details.get('vil') is not None:
                    address.append(details['vil'].title())
                if details.get('pay') is not None:
                    address.append(details['pay'].title())
                if len(address) > 0:
                    address = ' '.join(address)
                else:
                    address = None
                user = {'fullname': details.get('lib').split(' (').title(),
                        'id': details.get('url')[3:],
                        'avatar': details.get('img'),
                        'birthday': details.get('dat'),
                        'address': address,
                        'job': details['pro'],
                        'rels': []
                        }
                req = self.session.get(self._base_url + f"/p/{user['id']}/copains", timeout=60)
                if req.status_code != 200:
                    continue
                soup = BeautifulSoup(req.content, 'html.parser')
                for i in soup.find_all('a', attrs={'class': 'jTinyProfileUser notip'}):
                    uid = i['href'][3:]
                    name = i['title'].split(' (')[0].title()
                    user['rels'].append({'id': uid, 'fullname': name})
                results.append(user)
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


