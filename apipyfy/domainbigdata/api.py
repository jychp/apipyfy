import logging

import requests
from bs4 import BeautifulSoup

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-domainbigdata')


class DomainBigDataAPI(BaseAPI):
    """
    API for domainbigdata.com

    Retrieve related domain based on registrant information

    example:
        >>> api = DomainBigDataAPI()
        >>> for d in api.related_domains('domain.tld'):
        >>>    print(d)
        other_domain.tld
    """
    def __init__(self, user_agent='ApiPyFy/1.0.0', proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self.base_url = 'https://domainbigdata.com'

    def _make_request(self, search):
        try:
            payload = {'__EVENTTARGET': 'search',
                    '__EVENTARGUMENT': search}
            # Get formular data
            req = self.session.get(self.base_url, timeout=10)
            req.raise_for_status()
            soup = BeautifulSoup(req.content, 'html.parser')
            # Get __VIEWSTATE
            input = soup.find('input', attrs={'name': '__VIEWSTATE'})
            if input is None:
                logger.error('Can not find __VIEWSTATE value')
                return None
            payload['__VIEWSTATE'] = input['value']
            # Get __VIEWSTATEGENERATOR
            input = soup.find('input', attrs={'name': '__VIEWSTATEGENERATOR'})
            if input is None:
                logger.error('Can not find __VIEWSTATEGENERATOR value')
                return None
            payload['__VIEWSTATEGENERATOR'] = input['value']
            # Make post request
            req = self.session.post(self.base_url, data=payload, timeout=10)
            req.raise_for_status()
            return req.content
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

    def _parse_page(self, content):
        soup = BeautifulSoup(content, 'html.parser')
        for tr in soup.findAll('tr'):
            if not tr.get('id', '').startswith('MainMaster_rptWebsitesForName_trrptWebsitesForName_'):
                continue
            link = tr.find('a')
            if link is None:
                continue
            yield link.text.strip()

    def related_domains(self, domain_name):
        result = set()
        content = self._make_request(domain_name)
        if content is None:
            return None
        # Parse page
        soup = BeautifulSoup(content, 'html.parser')
        tr_ids = ['trRegistrantEmail', 'MainMaster_trRegistrantOrganization', 'trRegistrantName']
        for id in tr_ids:
            tr = soup.find('tr', attrs={'id': id})
            if tr is None:
                logger.debug(f"No tr found for {id}")
                continue
            td = tr.findAll('td')
            if len(td) < 3:
                logger.debug(f"Wrong structure for {id}")
                continue
            if td[2].text.strip() == 'is associated with 100+ domains':
                logger.debug(f"Skip {id} on too many domains")
                continue
            link = td[1].find('a')
            if link is None:
                continue
            req = self.session.get(self.base_url + link['href'], timeout=10)
            for i in self._parse_page(req.content):
                result.add(i)
        return list(result)
