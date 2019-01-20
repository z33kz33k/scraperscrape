import requests
from bs4 import BeautifulSoup
import json
import time
from pprint import pprint

from tscscrape.errors import PageWrongFormatError


URL = "http://www.skyscrapercenter.com/compare-data/submit?type%5B%5D=building&status%5B%5D=COM&status%5B%5D=UC&status%5B%5D=UCT&status%5B%5D=STO&base_region=0&base_country=0&base_city={}&base_height_range={}&base_company=All&base_min_year=1900&base_max_year=9999&comp_region=0&comp_country=0&comp_city=0&comp_height_range=4&comp_company=All&comp_min_year=1960&comp_max_year=2020&skip_comparison=on&output%5B%5D=list&dataSubmit=Show+Results"


def _scrape_citycodes():
    """Scrape available city codes into a dict to be saved as CITIES_CODES constant"""
    contents = requests.get(URL.format("All", "10")).text
    soup = BeautifulSoup(contents, "lxml")
    result = soup.find("select", id="base_city")
    result = result.find_all("option")
    return {tag.string: tag["value"] for tag in result}


def _scrape_heightranges():
    """Scrape available height ranges into a dict to be saved as HEIGHT_RANGES constant"""
    contents = requests.get(URL.format("All", "10")).text
    soup = BeautifulSoup(contents, "lxml")
    result = soup.find("select", id="base_height_range")
    result = result.find_all("option")
    return {tag.string: tag["value"] for tag in result}


# keys of below dicts are the same as options in "Base Data Range" form on the website
CITIES_CODES = _scrape_citycodes()
HEIGHT_RANGES = _scrape_heightranges()


def scrape_city(city, height_range="All", trim_heightless=True, floor=None):
    """Scrape city data"""
    keystr = "var buildings = "
    url = URL.format(CITIES_CODES[city], HEIGHT_RANGES[height_range])
    contents = requests.get(url).text
    soup = BeautifulSoup(contents, "lxml")
    try:
        result = next(resultset for resultset in soup.find_all("script", type="text/javascript")
                      if keystr in resultset.text)
    except StopIteration:
        raise ValueError(
            "Page for '{}' seems to have wrong format (missing '{}' string).\nFull URL: {}".format(city, keystr, url))
    result = result.text.strip()
    result = "".join(result.split(keystr)[1:])[:-1]
    result = json.loads(result)

    if trim_heightless:
        result = [city for city in result if city["height_architecture"] != "-"]

    if floor:
        result = [city for city in result if float(city["height_architecture"]) >= floor]

    return result


def scrape_allcities(height_range="All", trim_heightless=True, floor=None):
    """Scrape all cities data and dump it to file"""
    cities = {}
    for i, key in enumerate(key for key in CITIES_CODES.keys() if key != "All"):
        if i < 20:
            towers = scrape_city(key, height_range, trim_heightless, floor)
            if towers:
                cities.update({key: towers})
            print("{}: Scraped {} {} for '{}'...".format(
                str(i + 1).zfill(4),
                str(len(towers)),
                "towers" if len(towers) != 1 else "tower",
                key
            ))
            time.sleep(0.02)
        else:
            break

    with open("output/cities.json", mode="w") as jsonfile:
        json.dump(cities, jsonfile)


# result = scrape_city("London", "100m+", True)
# print(len(result))
# pprint(result)
