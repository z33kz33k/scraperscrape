"""

    tscscrape.debug
    ~~~~~~~~~~~~~~~~~
    Print and debug

"""

import os
import json
from pprint import pprint

from tscscrape.scraper import getcities


# TODO: testing and fleshing out


def print_city(city):
    """Print city data

    Arguments:
        city {str} -- a name of the city to print
    """

    # TODO: brief version of print output
    city = getcities(city_filter=city)
    print(str(city))
    for tower in city.towers:
        print()
        print(str(tower))


def print_country(country):
    pprint(sorted([(city.name, city.country, city.rating) for city
                   in getcities(country_filter=country)],
                  key=lambda triple: triple[2], reverse=True))


def print_region(region):
    pprint(sorted([(city.name, city.country, city.rating) for city
                   in getcities(region_filter=region)],
                  key=lambda triple: triple[2], reverse=True))
