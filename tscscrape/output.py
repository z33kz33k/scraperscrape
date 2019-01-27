"""

    tscscrape.output
    ~~~~~~~~~~~~~~~~~
    Print and create output files

"""

import os
import json
from contextlib import redirect_stdout
from pprint import pprint

from tscscrape.scraper import getcities, getcity, Country, Region, World
from tscscrape.utils import asteriskify, rightjustify
from tscscrape.constants import (REGIONMAP, OUTPUT_TXT_PATH, OUTPUT_TXT_REGIONS_PATH,
                                 OUTPUT_TXT_COUNTRIES_PATH, OUTPUT_TXT_CITIES_PATH,
                                 OUTPUT_JSON_PATH)
from tscscrape.countries import COUNTRYMAP
from tscscrape.errors import InvalidCountryError


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


def print_country(countryname, verbose=False):
    """Print country data

    Arguments:
        countryname {str} -- a name of the country to print

    Keyword Arguments:
        verbose {bool} -- a flag to switch the output's verbosity (default: {False})
    """
    cities = getcities(country_filter=countryname)
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


def print_region(region_name, verbose=False):
    """Print region data

    Arguments:
        region_name {str} -- a name of the region to print

    Keyword Arguments:
        verbose {bool} -- a flag to switch the output's verbosity (default: {False})
    """
    cities = getcities(region_filter=region_name)
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


def print_world(verbose=False):
    """Print world data

    Keyword Arguments:
        verbose {bool} -- a flag to switch the output's verbosity (default: {False})
    """
    world = World(getcities())
    max_countwidth = len(str(len(world.regions)))  # to right-justify output

    if verbose:
        print(world.getdescription())
    else:
        print(asteriskify(str(world)))
    for i, region in enumerate(world.regions):
        if verbose:
            print()
            print(region.getdescription())
        else:
            print(rightjustify("{}, {}".format(region.name, region.rating), i + 1,
                               max_countwidth))


def world_totxt():
    """Write world data to a .txt file
    """
    with open(os.path.join(OUTPUT_TXT_PATH, "world.txt"), mode="w") as f:
        with redirect_stdout(f):
            print_world()
            print()
            print(asteriskify("VERBOSE", 20))
            print()
            print_world(verbose=True)


def regions_totxt():
    """Write regions data to a .txt files
    """
    for region_name in REGIONMAP.values():
        path = os.path.join(OUTPUT_TXT_REGIONS_PATH, "{}.txt".format(region_name.replace(" ", "_")))
        with open(path, mode="w") as f:
            with redirect_stdout(f):
                print_region(region_name)
                print()
                print(asteriskify("DETAILS", 20))
                print()
                print_region(region_name, verbose=True)


def countries_totxt():
    """Write countries data to .txt files
    """
    country_names = [name for namelist in COUNTRYMAP.values() for name in namelist]

    for country_name in country_names:
        failed = False
        path = os.path.join(OUTPUT_TXT_COUNTRIES_PATH,
                            "{}.txt".format(country_name.replace(" ", "_")))
        with open(path, mode="w") as f:
            with redirect_stdout(f):
                try:
                    print_country(country_name)
                except InvalidCountryError:
                    failed = True
                if not failed:
                    print()
                    print(asteriskify("DETAILS", 20))
                    print()
                    print_country(country_name, verbose=True)
        if failed:
            os.remove(path)


def cities_totxt():
    """Write cities data to .txt files
    """
    city_names = [os.path.splitext(file)[0].replace("_", " ")
                  for _, _, files in os.walk(OUTPUT_JSON_PATH) for file in files]

    for city_name in city_names:
        path = os.path.join(OUTPUT_TXT_CITIES_PATH,
                            "{}.txt".format(city_name.replace(" ", "_")))
        with open(path, mode="w") as f, redirect_stdout(f):
            print_city(city_name)
            print()
            print(asteriskify("DETAILS", 20))
            print()
            print_city(city_name, verbose=True)
