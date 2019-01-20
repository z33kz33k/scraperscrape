import requests
from bs4 import BeautifulSoup
import os
import json

# parse application settings from "settings/settings.json"
with open(os.path.join("settings", "settings.json"), encoding="utf-8") as f:
    _settings = json.load(f)

CITIES_PATH = os.path.join(*_settings["cities_path"])
RATINGS_MATRIX = _settings["ratings_matrix"]

URL = "http://www.skyscrapercenter.com/compare-data/submit?type%5B%5D=building&status%5B%5D=COM&status%5B%5D=UC&status%5B%5D=UCT&status%5B%5D=STO&base_region=0&base_country=0&base_city={}&base_height_range={}&base_company=All&base_min_year=1900&base_max_year=9999&comp_region=0&comp_country=0&comp_city=0&comp_height_range=4&comp_company=All&comp_min_year=1960&comp_max_year=2020&skip_comparison=on&output%5B%5D=list&dataSubmit=Show+Results"


def _scrape_citycodes():
    """Scrape available city codes into a dict to be saved as CITIES_CODES constant."""
    contents = requests.get(URL.format("All", "10")).text
    soup = BeautifulSoup(contents, "lxml")
    result = soup.find("select", id="base_city")
    result = result.find_all("option")
    return {tag.string: tag["value"] for tag in result}


def _scrape_heightranges():
    """Scrape available height ranges into a dict to be saved as HEIGHT_RANGES constant."""
    contents = requests.get(URL.format("All", "10")).text
    soup = BeautifulSoup(contents, "lxml")
    result = soup.find("select", id="base_height_range")
    result = result.find_all("option")
    return {tag.string: tag["value"] for tag in result}


# keys of below dicts are the same as options in "Base Data Range" form on the website
CITIES_CODES = _scrape_citycodes()
HEIGHT_RANGES = _scrape_heightranges()
