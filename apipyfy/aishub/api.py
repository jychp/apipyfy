import requests
import time
import logging

logger = logging.getLogger('apipyfy-aishub')


class AisHubAPI:
    """
    API for aishub.net

    Retrieve Ships from AIS position

    example:
        >>> api = AisHubAPI()
        >>> for mmsi, data in api.get_ships(lat, lon).items():
        >>>    print(mmsi, data)
        228244600 {'ship_name': 'ND RUMENGOL', 'positions': [{'lat': '48.39272', 'lon': '-4.42883', 'cog': 360, 'sog': 0}]}
    """
    def __init__(self, user_agent='ApiPyFy/1.0.0', proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self.session.headers.update({'Accept': 'application/json, text/javascript, */*; q=0.01',
                                     'X-Requested-With': 'XMLHttpRequest'})
        
    def _get_stations(self, lat, lon):
        results = []
        try:
            payload =  {'minLat': lat - 0.2, 
                        'maxLat': lat + 0.2, 
                        'minLon': lon - 0.9, 
                        'maxLon': lon + 0.9,
                        'zoom': 10,
                        't': int(time.time()),
                        'view': 'false'}
            req = self.session.get('https://www.aishub.net/coverage.json', params=payload, timeout=5)
            req.raise_for_status()
            for s in req.json()['stations']:
                lat = float(s['lat'])
                lon = float(s['lon'])
                if lat > lat + 0.2:
                    continue
                if lat < lat - 0.2:
                    continue
                if lon > lon + 0.9:
                    continue
                if lon < lon - 0.9:
                    continue
                results.append(s)
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
        return results
            
    def get_ships(self, minLat, maxLat, minLon, maxLon):
        results = {}
        try:
            stations = self._get_stations(minLat, maxLat, minLon, maxLon)
            logger.debug(f'Found {len(stations)} stations')
            for station in stations:
                payload =  {'minLat': minLat, 
                            'maxLat': maxLat, 
                            'minLon': minLon, 
                            'maxLon': maxLon,
                            'zoom': 10,
                            'mode': 'number',
                            't': int(time.time()),
                            'view': 'true'}
                req = self.session.get(f"https://www.aishub.net/station/{station['id']}/map.json", params=payload, timeout=5)
                req.raise_for_status()
                for p in req.json()['positions']:
                    try:
                        results[p['mmsi']]['positions'].append({'lat': p['lat'], 'lon': p['lon'], 'cog': p['cog'], 'sog': p['sog']})
                    except KeyError:
                        results[p['mmsi']] = {'ship_name': p['ship_name'], 'positions': []}
                        results[p['mmsi']]['positions'].append({'lat': p['lat'], 'lon': p['lon'], 'cog': p['cog'], 'sog': p['sog']})
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
