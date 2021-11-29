import logging

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse as dt_parse

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-skypli')


class SkypliAPI(BaseAPI):
    """
    API for https://www.skypli.com

    Retrieve Personnal info from Skype Account

    example:
        >>> api = SkypliAPI()
        >>> for p in api.search('John Doe'):
        >>>    print(p)
        {'id': 'john.doe42', 'fullname': 'John Doe', 'avatar': '/assets/images/no_image.jpg', 'address': 'Paris France', 'gender': 'male', 'birthday': datetime('1946-02-08')}    
    """
    def __init__(self, user_agent=None, proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self._base_url = 'https://www.skypli.com'

    def search(self, full_name):
        try:
            results = []
            req = self.session.get(f"{self._base_url}/search/{full_name}", timeout=60)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            for div in soup.find_all('div', attrs={'class': 'search-results__block-info'}):
                user = {'id': None,
                        'fullname': None,
                        'avatar': None,
                        'address': None,
                        'gender': None,
                        'birthday': None}
                # Parse
                spans = div.find_all('span')
                if len(spans) != 2:
                    continue
                full_id = spans[0].text.strip()
                if full_id.startswith('live:'):
                    user['id'] = full_id[5:]
                else:
                    user['id'] = full_id
                user['fullname'] = spans[1].text.strip().title()
                # Get profile
                req2 = self.session.get(f"{self._base_url}/profile/{full_id}", timeout=60)
                req2.raise_for_status()
                soup2 = BeautifulSoup(req2.content, 'html.parser')
                # Find avatar
                avatar_div = soup2.find('div', attrs={'class': 'profile-box__info-image'})
                user['avatar'] = avatar_div['style'].split("url('")[-1][:-2]
                # Find data
                address = []
                for row in soup2.find_all('div', attrs={'class': 'profile-box__table-row'}):
                    divs = row.find_all('div')
                    if len(divs) != 2:
                        continue
                    
                    k = divs[0].text.strip()
                    v = divs[1].text.strip()
                    if k == 'City':
                        address.append(v.title())
                    elif k == 'Country':
                        address.append(v.title())
                    elif k == 'Birthday':
                        user['birthday'] = dt_parse(v)
                    elif k == 'Gender':
                        user['gender'] = v.lower()
                if len(address) > 0:
                    user['address'] = ' '.join(address)
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
