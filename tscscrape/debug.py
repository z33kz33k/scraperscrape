"""

    tscscrape.debug
    ~~~~~~~~~~~~~~~~~
    Print and debug

"""

import os
import json
from pprint import pprint

from tscscrape.scraper import getcities, getcity, Country, Region
from tscscrape.utils import asteriskify, rightjustify


# TODO: testing and fleshing out


def print_city(cityname, verbose=False):
    """Print city data

    Arguments:
        cityname {str} -- a name of the city to print

    Keyword Arguments:
        verbose {bool} -- a flag to switch the output's verbosity (default: {False})
    """
    city = getcity(cityname)
    max_countwidth = len(str(len(city.towers)))  # to right-justify output

    if verbose:
        print(city.getdescription())
    else:
        print(asteriskify((str(city))))
    for i, tower in enumerate(city.towers):
        if verbose:
            print()
            print(tower.getdescription())
        else:
            print(rightjustify(str(tower), i + 1, max_countwidth))


def print_country(country, verbose=False):
    cities = getcities(country_filter=country)
    countryname = cities[0].country
    country = Country(countryname, cities)
    max_countwidth = len(str(len(cities)))  # to right-justify output

    if verbose:
        print(country.getdescription())
    else:
        print(asteriskify(str(country)))
    for i, city in enumerate(cities):
        if verbose:
            print()
            print(city.getdescription())
        else:
            print(rightjustify("{}, {}".format(city.name, city.rating), i + 1, max_countwidth))


# TODO
# def print_region(region):
#     cities = getcities(region_filter=region)
#     pprint(sorted([(city.name, city.country, city.rating) for city
#                    in getcities(region_filter=region)],
#                   key=lambda triple: triple[2], reverse=True))
