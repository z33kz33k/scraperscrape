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


def print_region(region, verbose=False):
    cities = getcities(region_filter=region)
    region_name = cities[0].region
    region = Region(region_name, cities)
    max_countwidth = len(str(len(region.countries)))  # to right-justify output

    if verbose:
        print(region.getdescription())
    else:
        print(asteriskify(str(region)))
    for i, country in enumerate(region.countries):
        if verbose:
            print()
            print(country.getdescription())
        else:
            print(rightjustify("{}, {}".format(country.name, country.rating), i + 1,
                               max_countwidth))
