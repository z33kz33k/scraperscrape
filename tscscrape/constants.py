"""

    tscscrape.constants
    ~~~~~~~~~~~~~~~~~~~
    Constants to import in other modules

"""

import requests
from bs4 import BeautifulSoup
import os
import json

# parse application settings from "settings/settings.json"
with open(os.path.join("settings", "settings.json"), encoding="utf-8") as f:
    _settings = json.load(f)

URL = _settings["url"]
CITIES_PATH = os.path.join(*_settings["cities_path"])
REGIONS_PATH = os.path.join(*_settings["regions_path"])
RATINGS_MATRIX = _settings["ratings_matrix"]
STATUS = _settings["status"]
REGIONS = _settings["regions"]

# TODO: change it to scrape it locally (to not get blacklisted by the server)


def _scrape_cities():
    """Scrape city codes to be entered in URL."""
    contents = requests.get(URL.format("All", "10")).text
    soup = BeautifulSoup(contents, "lxml")
    result = soup.find("select", id="base_city")
    result = result.find_all("option")
    return {tag.string: tag["value"] for tag in result}


def _scrape_heightranges():
    """Scrape codes of height ranges to be entered in URL."""
    contents = requests.get(URL.format("All", "10")).text
    soup = BeautifulSoup(contents, "lxml")
    result = soup.find("select", id="base_height_range")
    result = result.find_all("option")
    return {tag.string: tag["value"] for tag in result}


# keys of below dicts are the same as options in "Base Data Range" form on the website
CITIES = _scrape_cities()
HEIGHT_RANGES = _scrape_heightranges()
