import logging

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse as dt_parse

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-societeninja')


class SocieteNinjaAPI(BaseAPI):
    """
    API for https://www.societe.ninja

    Retrieve Company information

    example:
        >>> api = SocieteNinjaAPI()
        >>> for p in api.search_company('EvilCorp'):
        >>>    print(p)
        {'name': 'EvilCorp', 'siren': '123456789', 'hq': '1 AVENUE DU PARADIS PARIS', 'kind': 'SAS, société par actions simplifiée', 'capital': '1 500,00 EUR', 'naf': '68.31Z', 'activity': 'Agences immobilières', 'tva': 'FR46883836819', 'leaders': [{'name': 'John Doe', 'comment': 'Né(e) le 01/04/1972 à Paris 12 chemin de Traverse Londres'}], 'owners': [], 'employes': [], 'creation_date': datetime.datetime(2020, 5, 26, 0, 0)}
        >>> api.search_leader('John Doe')
        >>> api.company_details('123456789')
    """
    def __init__(self, user_agent=None, proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self._base_url = 'https://societe.ninja'

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
            # Make request
            params = {'siren': siren}
            req = self.session.get(self._base_url + '/data.php', params=params, timeout=60)
            req.raise_for_status()
            # parse
            soup = BeautifulSoup(req.content, 'html.parser')
            # Legal
            legal = soup.find(id='menu_unite_legale')
            tbody = legal.find('tbody')
            for tr in tbody.find_all('tr'):
                tds = tr.find_all('td')
                k = tds[0].text.strip()
                d = []
                for i in tds[1].text.strip().split('\n'):
                    d.append(i.strip())
                v = ' '.join(d)
                if k == "Dénomination Sociale":
                    result['name'] = v.title()
                elif k == 'Siège Social':
                    result['hq'] = v
                elif k == 'Forme Juridique':
                    result['kind'] = v
                elif k == 'Capital Social':
                    result['capital'] = v
                elif k == 'Immatriculation':
                    result['creation_date'] = dt_parse(v)
                elif k == 'Code NAF':
                    result['naf'] = v
                elif k == 'Activité':
                    result['activity'] = v
                elif k == 'TVA Intracommunautaire':
                    result['tva'] = v
            # Leaders
            leaders = soup.find(id='menu_representants')
            if leaders is not None:
                tbody = leaders.find('tbody')
                for tr in tbody.find_all('tr'):
                    tds = tr.find_all('td')
                    data = list(tds[-1].children)
                    name = data[0].strip().title().replace('  ',' ')
                    info = []
                    for i in data[1:]:
                        i = str(i).strip()
                        if i == '<br/>':
                            continue
                        info.append(i)
                    result['leaders'].append({'name': name, 'comment': ' '.join(info)})
            # Owners
            owners = soup.find(id='menu_beneficiaires')
            if owners is not None:
                tbody = owners.find('tbody')
                for tr in tbody.find_all('tr'):
                    tds = tr.find_all('td')
                    data = list(tds[0].children)
                    name = data[0].text.strip().title().replace('  ',' ')
                    info = []
                    for i in data[1:]:
                        i = str(i).strip()
                        if i == '<br/>':
                            continue
                        info.append(i)
                    result['owners'].append({'name': name, 'comment': ' '.join(info)})
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


    def search_leader(self, search, page=1):
        results = []
        try:
            # Make request
            params = {'dirigeant': search, 'page': page}
            req = self.session.get(f"{self._base_url}/dirigeant.php", params=params, timeout=60)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            tbody = soup.find('tbody')
            if tbody is None:
                return results
            # Parse
            count = 0
            for tr in tbody.find_all('tr'):
                count += 1
                tds = tr.find_all('td')
                siren = tds[1].text.strip()
                details = self.company_details(siren)
                if details is not None:
                    results.append(details)
                
            if count >= 20 and page <= 3:
                data = self.search_leader(search, page=page+1)
                if data is None:
                    return None
                results += data
            
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

    def search_company(self, company_name, page=1):
        results = []
        try:
            # Make request
            params = {'denomination': company_name, 'page': page}
            req = self.session.get(f"{self._base_url}/results.php", params=params, timeout=60)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            tbody = soup.find('tbody')
            if tbody is None:
                return results
            # Parse
            count = 0
            for tr in tbody.find_all('tr'):
                count += 1
                tds = tr.find_all('td')
                siren = tds[1].text.strip()
                details = self.company_details(siren)
                if details is not None:
                    results.append(details)
                
            if count >= 20 and page <= 3:
                data = self.search_leader(company_name, page=page+1)
                if data is None:
                    return None
                results += data
            
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
