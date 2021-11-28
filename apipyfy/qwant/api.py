import logging

import requests

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-qwant')


class QwantAPI(BaseAPI):
    """
    API for https://www.qwant.com

    Search engine

    example:
        >>> api = QwantAPI()
        >>> for p in api.search('site:linkedin.com/in/ "John Doe"'):
        >>>    print(p)
        {'title': 'John Doe - Pentester.', 'favicon': 'https://s.qwant.com/fav/l/i/fr_linkedin_com.ico', 'url': 'https://fr.linkedin.com/in/john-doe', 'desc': 'Consultez le profil de John Doe sur LinkedIn, le plus grand réseau professionnel mondial. La formation de John Doe est indiquée sur son profil. Consultez le profil complet sur LinkedIn et découvrez les relations de John Doe, ainsi que des emplois dans des entreprises similaires.'}
    """
    def __init__(self, user_agent=None, proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self._base_url = 'https://www.qwant.com'
        self._api_url = 'https://api.qwant.com/v3/search/web'

    def search(self, search, lang='fr', locale='fr_FR', max_results=20):
        results = []
        try:
            # Init
            params = {'lang': lang,
                      'q': search,
                      't': 'web'}
            req = self.session.get(self._base_url, params=params, timeout=60)
            req.raise_for_status()
            # Search
            page = 0
            while len(results) <= max_results:
                params = {'q': search,
                          'count': 10,
                          'locale': locale,
                          'offset': page * 10,
                          'device': 'desktop',
                          'safesearch': 1}
                req = self.session.get(self._api_url, params=params, timeout=60)
                req.raise_for_status()
                data = req.json()['data']['result']
                for i in data['items']['mainline']:
                    if i['type'] != 'web':
                        continue
                    for j in i['items']:
                        results.append({'title': j['title'],
                                        'favicon': j['favicon'],
                                        'url': j['url'],
                                        'desc': j['desc']})
                page += 1
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
