import googlemaps
from dotenv import dotenv_values


googlemaps_api_key = dotenv_values(".env").get('GOOGLE_MAPS_API_KEY')


def get_coordinates_by_search_query(address):
    gmaps_client = googlemaps.Client(googlemaps_api_key)
    geocode_result = gmaps_client.geocode(address)
    #return geocode_result[0]
    print(geocode_result)
    return geocode_result[0]["geometry"]["location"]

