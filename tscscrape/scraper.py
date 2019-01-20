import requests
from bs4 import BeautifulSoup
import json
import time
import os
from pprint import pprint

from tscscrape.constants import URL, CITIES_CODES, HEIGHT_RANGES
from tscscrape.errors import PageWrongFormatError
from tscscrape.utils import timestamp


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
        raise PageWrongFormatError(
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
    for i, key in enumerate(key for key in CITIES_CODES.keys() if key != "All"):
        if i in range(100, 110):
            try:
                towers = scrape_city(key, height_range, trim_heightless, floor)
            except PageWrongFormatError:
                towers = []
            if towers:
                data = {
                    "timestamp": timestamp(),
                    "towers": towers
                }
                destpath = os.path.join("output", "cities", "{}.json".format(key.replace(" ", "_")))
                with open(destpath, mode="w") as jsonfile:
                    json.dump(data, jsonfile)
            print("{}: Scraped {} {} for '{}'...".format(
                str(i + 1).zfill(4),
                str(len(towers)),
                "towers" if len(towers) != 1 else "tower",
                key
            ))
            time.sleep(0.02)
