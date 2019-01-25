"""

    tscscrape.debug
    ~~~~~~~~~~~~~~~~~
    Print and debug

"""

import os
import json

from tscscrape.constants import CITIES_PATH
from tscscrape.scraper import City


def print_city(city):
    """Print city data

    Arguments:
        city {str} -- a name of the city to print
    """

    path = os.path.join(CITIES_PATH, city.replace(" ", "_") + ".json")
    with open(path) as f:
        data = json.load(f)

    city = City(data)
    print(str(city))
    for tower in city.towers:
        print()
        print(str(tower))
