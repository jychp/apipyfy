import logging
import math

import requests

from apipyfy.base import BaseAPI

logger = logging.getLogger('apipyfy-marinetraffic')


class MarineTrafficAPI(BaseAPI):
    """
    API for marinetraffic.com

    Retrieve Ships from AIS position

    example:
        >>> api = MarineTrafficAPI()
        >>> for ship in api.get_ships(lat, lon):
        >>>    print(ship)
        {'LAT': '48.11261', 'LON': '-5.08825', 'SPEED': '62', 'COURSE': '244', 'HEADING': None, 'ELAPSED': '1281', 'DESTINATION': 'CLASS B', 'FLAG': 'NO', 'LENGTH': '13', 'SHIPNAME': 'PATPICHA', 'SHIPTYPE': '9', 'SHIP_ID': '310662', 'WIDTH': '4', 'L_FORE': '10', 'W_LEFT': '2'}
    """
    def __init__(self, user_agent='ApiPyFy/1.0.0', proxy=None) -> None:
        super().__init__(user_agent, proxy)
        self.session.headers.update({'Accept': 'application/json, text/javascript, */*; q=0.01',
                                     'X-Requested-With': 'XMLHttpRequest'})

    def deg_to_tiles(self, lat, lon, zoom=10):
        lat_rad = math.radians(lat)
        n = 2.0 ** (zoom - 1)
        xtile = int((lon + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        return xtile, ytile

    def get_ships(self, lat, lon):
        results = []
        try:
            # Get page
            page_url = f"https://www.marinetraffic.com/en/ais/home/centerx:{lon}/centery:{lat}/zoom:10"
            req = self.session.get(page_url, timeout=10)
            req.raise_for_status()
            # Calculate boxes
            minLat = lat - 0.2
            maxLat = lat + 0.2
            minLon = lon - 0.90
            maxLon = lon + 0.90
            start_x, start_y = self.deg_to_tiles(minLat, minLon)
            stop_x, stop_y = self.deg_to_tiles(maxLat, maxLon)
            x_borders = sorted([start_x, stop_x])
            y_borders = sorted([start_y, stop_y])
            # Get XHR
            for y in range(y_borders[0], y_borders[1] + 1):
                for x in range(x_borders[0], x_borders[1] + 1):
                    print(x, y)
                    xhr_url = f"https://www.marinetraffic.com/getData/get_data_json_4/z:10/X:{x}/Y:{y}/station:0"
                    req = self.session.get(xhr_url, timeout=5)
                    if req.status_code == 403:
                        print(403)
                        continue
                    for s in req.json()['data']['rows']:
                        results.append(s)
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
