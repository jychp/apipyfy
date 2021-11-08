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

    def get_ships(self, lat, lon, zoom=10):
        results = []
        try:
            # Get page
            page_url = f"https://www.marinetraffic.com/en/ais/home/centerx:{lon}/centery:{lat}/zoom:{zoom}"
            req = self.session.get(page_url, timeout=10)
            req.raise_for_status()
            # Calculate boxes
            # delta_Lon=757.28*math.exp(-0.728*zoom)/2
            # delta_Lat=1291.5*math.exp(-0.681*zoom)/2
            # minLat = lat - delta_Lat
            # maxLat = lat + delta_Lat
            # minLon = lon - delta_Lon
            # maxLon = lon + delta_Lon
            center_x, center_y = self.deg_to_tiles(lat, lon, zoom)

            # start_x, start_y = self.deg_to_tiles(minLat, minLon, zoom)
            # stop_x, stop_y = self.deg_to_tiles(maxLat, maxLon, zoom)
            # x_borders = sorted([start_x, stop_x])
            # y_borders = sorted([start_y, stop_y])
            # Get XHR
            for y in (center_y - 1, center_y, center_y + 1):
                print(y)
                for x in (center_x - 1, center_x, center_x + 1):
                    xhr_url = f"https://www.marinetraffic.com/getData/get_data_json_4/z:{zoom}/X:{x}/Y:{y}/station:0"
                    req = self.session.get(xhr_url, timeout=5)
                    if req.status_code == 403:
                        logger.debug(f"Error 403 for tile {x},{y}")
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
