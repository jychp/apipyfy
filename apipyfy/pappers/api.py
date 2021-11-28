import logging
import re

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse as dt_parse

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-pappers')
REGEX_BIRTHDAY = re.compile(r'^.*date_de_naissance_dirigeant_min=(\d{2}-\d{2}-\d{4}).*date_de_naissance_dirigeant_max=(\d{2}-\d{2}-\d{4})$')


class PappersAPI(BaseAPI):
    """
    API for https://www.pappers.fr

    Retrieve Company information

    example:
        >>> api = PappersAPI()
        >>> for p in api.search('EvilCorp'):
        >>>    print(p)
        {'name': 'EvilCorp', 'siren': '123456789', 'hq': '1 AVENUE DU PARADIS PARIS', 'kind': 'SAS, société par actions simplifiée', 'capital': '1 500,00 EUR', 'naf': '68.31Z', 'activity': 'Agences immobilières', 'tva': 'FR46883836819', 'leaders': [{'name': 'John Doe', 'comment': 'Né(e) le 01/04/1972 à Paris 12 chemin de Traverse Londres'}], 'owners': [], 'employes': [], 'creation_date': datetime.datetime(2020, 5, 26, 0, 0)}
        >>> api.search('John Doe')
        >>> api.company_details('123456789')
    """
    def __init__(self, user_agent=None, proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self._base_url = 'https://www.pappers.fr'
        self._api_url = 'https://api.pappers.fr/v2'
        self._api_token = '97a405f1664a83329a7d89ebf51dc227b90633c4ba4a2575'

    def search(self, search, page=1):
        results = []
        try:
            req = self.session.get(self._base_url)
            req.raise_for_status()
            params = {'q': search,
                      'code_naf': '',
                      'api_token': self._api_token,
                      'precision': 'standard',
                      'bases': 'entreprises,dirigeants,beneficiaires,publications',
                      'page': page,
                      'par_page': 20}
            req = self.session.get(self._api_url + '/recherche', params=params)
            req.raise_for_status()  
            data = req.json()
            
            for k in data['resultats']:
                c = self.company_details(k['siren'])
                if c is not None:
                    results.append(c)

            if data['total'] > 20 * page:
                r = self.search(search, page=page+1)
                if r is None:
                    return None
                results += r
            
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

    def company_details(self, siren):
        result = {
            'name': None,
            'siren': siren,
            'hq': None,
            'kind': None,
            'capital': None,
            'naf': None,
            'activity': None,
            'tva': None,
            'creation_date': None,
            'leaders': [],
            'owners': [],
            'employes': []
        }
        try:
            params = {'q': siren}
            req = self.session.get(self._base_url + '/recherche', params=params)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            # Name
            div = soup.find('div', attrs={'class': 'nom-siren'})
            if div is not None:
                h1 = div.find('h1')
                if h1 is not None:
                    result['name'] = h1.text.strip().title()
            # Main data
            div = soup.find('div', attrs={'class': 'infos-princi'})
            if div is not None:
                for sub_div in div.find_all('div'):
                    p = sub_div.find_all('p')
                    if len(p) != 2:
                        continue
                    k = p[0].text.strip()
                    v = p[1].text.split('\n')[0].strip()
                    # Parse
                    if k == 'Adresse :':
                        result['hq'] = v
                    elif k == 'Activité :':
                        result['kind'] = v
                    elif k == 'Création :':
                        result['creation_date'] = dt_parse(v)
            # Juridique
            table = soup.find('table', attrs={'class': 'info-juridiques'})
            if table is not None:
                for tr in table.find_all('tr'):
                    th = tr.find('th')
                    td = tr.find('td')  
                    k = th.text.strip()
                    v = td.text.split('\n')[0].strip()
                    if k == 'SIREN :':
                        result['siren'] = v.replace(' ', '')
                    elif k == 'Forme juridique :':
                        result['kind'] = v
                    elif k == 'TVA intracommunautaire :':
                        result['tva'] = v
                    elif k == 'Capital social :':
                        result['capital'] = v          
            # Leaders
            ul = soup.find('ul', attrs={'class': 'dirigeant'})
            for a in ul.find_all('a'):
                name = a.text.strip().title()
                comment = None
                t = REGEX_BIRTHDAY.match(a['href'])
                if t is not None:
                    dates = t.groups()
                    if dates[0] == dates[1]:
                        comment = f'Né le {dates[0]}'
                result['leaders'].append({'name': name, 'comment': comment})
            # Owners
            section = soup.find(id='beneficiaires')
            for a in section.find_all('a'):
                name = a.text.strip().title()
                comment = None
                t = REGEX_BIRTHDAY.match(a['href'])
                if t is not None:
                    dates = t.groups()
                    if dates[0] == dates[1]:
                        comment = f'Né le {dates[0]}'
                result['owners'].append({'name': name, 'comment': comment})   

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
