import geoip2.database
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class LocationService:
    def __init__(self):
        self.reader = geoip2.database.Reader(os.path.join(BASE_DIR, 'corpo/static/geolite.mmdb'))

    def get_location(self, ip_address):
        try:
            response = self.reader.city(ip_address)
            return str(response.city.name) + ', ' + str(response.subdivisions.most_specific.name) + ' - ' + str(response.country.name)
        except geoip2.errors.AddressNotFoundError:
            return "rastreamento sem exito"