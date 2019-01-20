"""

    tscscrape.regions
    ~~~~~~~~~~~~~~~~~
    Scrape region metadata from sources other than TSC (it's unavailable in skyscrapers data)

"""

import os
from bs4 import BeautifulSoup, NavigableString
from pprint import pprint

from tscscrape.constants import REGIONS_PATH

WIKIPEDIA_CA_COUNTRIES = ["Belize", "Costa Rica", "El Salvador",
                          "Guatemala", "Honduras", "Nicaragua", "Panama"]


def scrape_countries(filename):
    """Scrape country names from locally saved Wikipedia pages."""
    def filter_search(tag):
        children = tag.children
        return tag.name == "td" and tag.has_attr("align") and tag.find("a") and tag.find("span") and not any(isinstance(child, NavigableString) for child in children)

    path = os.path.join(REGIONS_PATH, filename)
    with open(path) as file:
        contents = "\n".join(file.readlines())
    soup = BeautifulSoup(contents, "lxml")
    tds = soup.find_all(filter_search)

    countries = []
    for td in tds:
        element = td.find("a")
        countries.append(element.string)

    return sorted(countries)


def get_ca_countries():
    """Get names of Central-American countries."""
    caribbean = scrape_countries("caribbean.html")
    ca_countries = [c for c in caribbean if c not in WIKIPEDIA_CA_COUNTRIES]
    ca_countries.extend(WIKIPEDIA_CA_COUNTRIES)
    return sorted(ca_countries)
