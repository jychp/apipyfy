import logging

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse as dt_parse

from apipyfy.base import BaseAPI


logger = logging.getLogger('apipyfy-wikileaks')


class WikileaksAPI(BaseAPI):
    """
    API for wikileaks.org

    Retrieve leaks from any search

    example:
        >>> api = WikileaksAPI()
        >>> for r in api.search('facebook.com', max_results=20):
        >>> print(r)
        {'url': 'https://wikileaks.org/opcw-douma/document/RedactedInterimReport/', 'title': 'WikiLeaks - RedactedInterimReport', 'leak': 'OPCW Douma Docs', 'summary': '... status/982854571952431104    \uf0b7 https://twitter.com/KokachOmar/status/982851902223286272    \uf0b7 https ... -180407135235699.html    \uf0b7 https://m.facebook.com/story.php? story_fbid= ... -idUSKBN1HF09Z    \uf0b7 https://twitter.com/AsaadHannaa/status/982998575222312961  \uf0b7 http ...', 'released_date': datetime.datetime(2019, 10, 23, 0, 0)}
    """
    def __init__(self, user_agent='ApiPyFy/1.0.0', proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self._base_url = 'https://search.wikileaks.org'

    def search(self, search, page=1, max_results=20):
        result = []
        try:
            payload = {'query': '',
                    'exact_phrase': search,
                    'any_of': '',
                    'exclude_words': '',
                    'document_date_start': '',
                    'document_date_end': '',
                    'released_date_start': '',
                    'released_date_end': '',
                    'new_search': True,
                    'page': page,
                    'order_by': 'newest_released_date'}
            req = self.session.get(self._base_url, params=payload, timeout=5)
            req.raise_for_status()
            # Check for refresh
            soup = BeautifulSoup(req.text, 'html.parser')
            for div in soup.findAll('div', attrs={'class': 'result'}):
                r = {'url': None, 'title': None, 'leak': None, 'summary': None, 'released_date': None}
                h4 = div.find('h4')
                a = h4.find('a')
                r['url'] = a['href']
                r['title'] = a.text.strip()
                title_div = div.find('div', attrs={'class': 'leak-label'})
                r['leak'] = title_div.text.strip()
                summary_div = div.find('div', attrs={'class': 'excerpt'})
                r['summary'] = summary_div.text.strip()
                for d in div.findAll('div', attrs={'class': 'date'}):
                    if 'Released' not in d.text:
                        continue
                    d_span = d.find('span')
                    r['released_date'] = dt_parse(d_span.text.strip())
                result.append(r)
                
                if len(result) >= max_results:
                    return result

            pagination = soup.find('ul', attrs={'class': 'pagination'})
            if pagination is not None:
                li = pagination.findAll('li')[-1]
                a = li.find('a')
                for t in a['href'].split('&'):
                    if not t.startswith('page='):
                        continue
                    next_page = int(t.split('=')[-1])
                    if next_page > page:
                        result += self.search(search, next_page)
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
