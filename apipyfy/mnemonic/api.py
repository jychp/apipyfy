import datetime
import urllib3
import logging

import requests

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-mnemonic')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class MnemonicAPI(BaseAPI):
    """
    API for passivedns.mnemonic.no

    Retrieve DNS history

    example:
        >>> api = MnemonicAPI()
        >>> for d in api.history_dns('1.1.1.1'):
        >>>    print(d)
        {'domain': 'domain.tld', 'target': '1.1.1.1', 'type': 'a', 'date': <datetime>}
    """
    def __init__(self, user_agent=None, proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self.session.headers.update({'Host': 'api.mnemonic.no',
                                     'Accept': 'application/json',
                                     'Accept-Encoding': 'gzip, deflate, br',
                                     'Accept-Language': 'en-US;q=0.7,en;q=0.3',
                                     'Cache-Control': 'no-cache',
                                     'Connection': 'keep-alive',
                                     'content-type': 'application/json',
                                     'DNT': '1',
                                     'origin': 'https://passivedns.mnemonic.no',
                                     'Pragma': 'no-cache',
                                     'Referer': 'https://passivedns.mnemonic.no/'})
        self._payload = {'aggregateResult': True,
                         'customerID': [],
                         'includeAnonymousResults': True,
                         'limit': 250,
                         'offset': 0,
                         'query': '',
                         'rrClass': [],
                         'rrType': [],
                         'tlp': []}
        self._base_url = 'https://94.127.60.190/pdns/v3/search'

    def history_dns(self, value) -> list:
        results = []
        try:
            self._payload['query'] = value
            req = self.session.post(self._base_url,
                                    json=self._payload,
                                    verify=False,
                                    timeout=5)
            req.raise_for_status()
            jsonreq = req.json()
            data = jsonreq.get('data')
            if data is None:
                return
            for entry in data:
                entry_date = datetime.datetime.fromtimestamp(int(entry['lastSeenTimestamp']) / 1000)
                results.append({'domain': entry['query'],
                                'target': entry['answer'],
                                'type': entry['rrtype'],
                                'date': entry_date})
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
