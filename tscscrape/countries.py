"""

    tscscrape.countries
    ~~~~~~~~~~~~~~~~~
    Scrape countries metadata from sources other than TSC (it's unavailable in skyscrapers data)

"""

import os
from bs4 import BeautifulSoup, NavigableString
from pprint import pprint

from tscscrape.utils import readinput
from tscscrape.constants import INPUT_PATH


WIKIPEDIA_CA_COUNTRIES = ["Belize", "Costa Rica", "El Salvador",
                          "Guatemala", "Honduras", "Nicaragua", "Panama"]


def _scrape_countries(filename):
    """Scrape country names from locally saved Wikipedia pages."""
    def filter_search(tag):
        children = tag.children
        return tag.name == "td" and tag.has_attr("align") and tag.find("a") and tag.find("span") and not any(isinstance(child, NavigableString) for child in children)

    contents = readinput(filename)
    soup = BeautifulSoup(contents, "lxml")
    tds = soup.find_all(filter_search)

    countries = []
    for td in tds:
        element = td.find("a")
        countries.append(element.string)

    return sorted(countries)


def _get_ca_countries():
    """Get names of Central-American countries."""
    caribbean = _scrape_countries("caribbean.html")
    ca_countries = [c for c in caribbean if c not in WIKIPEDIA_CA_COUNTRIES]
    ca_countries.extend(WIKIPEDIA_CA_COUNTRIES)
    return sorted(ca_countries)


def get_countries_by_region():
    """Get countries names lists grouped by region (i.e. continent).

    Overlaps:
    ~~~~~~~~~
    Europe-Asia
    ['Armenia', 'Azerbaijan', 'Georgia', 'Kazakhstan', 'Russia', 'Turkey']
    Europe-Africa
    []
    Africa-Asia
    []
    North America-South America
    []
    North America-Central America
    ['Antigua and Barbuda',
    'Bahamas',
    'Barbados',
    'Belize',
    'Costa Rica',
    'Cuba',
    'Dominica',
    'Dominican Republic',
    'El Salvador',
    'Grenada',
    'Guatemala',
    'Haiti',
    'Honduras',
    'Jamaica',
    'Nicaragua',
    'Panama',
    'Saint Kitts and Nevis',
    'Saint Lucia',
    'Saint Vincent and the Grenadines',
    'Trinidad and Tobago']
    South America-Central America
    ['Guyana', 'Suriname']
    Oceania-Asia
    []
    Middle East-Europe
    ['Turkey']
    Middle East-Africa
    []
    Middle East-Asia
    ['Bahrain',
    'Iran',
    'Iraq',
    'Israel',
    'Jordan',
    'Kuwait',
    'Lebanon',
    'Oman',
    'Qatar',
    'Saudi Arabia',
    'Syria',
    'Turkey',
    'United Arab Emirates',
    'Yemen']
    """
    europe = _scrape_countries("europe.html")
    asia = _scrape_countries("asia.html")
    africa = _scrape_countries("africa.html")
    namerica = _scrape_countries("north_america.html")
    samerica = _scrape_countries("south_america.html")
    camerica = _get_ca_countries()
    oceania = _scrape_countries("oceania.html")
    meast = _scrape_countries("middle_east.html")

    return {
        "EU": sorted([c for c in europe if c not in asia] + ["Russia"]),
        "NA": [c for c in namerica if c not in camerica],
        "CA": [c for c in camerica if c not in samerica] + ["Puerto Rico"],
        "SA": samerica,
        "AF": africa + ["Congo"],
        "ME": meast,
        "AS": [c for c in asia if c not in meast and c != "Russia"],
        "OC": oceania
    }


COUNTRYMAP = get_countries_by_region()
