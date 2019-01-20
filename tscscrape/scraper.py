import requests
from bs4 import BeautifulSoup
import json
import time
import os
from collections import Counter
from pprint import pprint

from tscscrape.constants import URL, CITIES_CODES, HEIGHT_RANGES, CITIES_PATH, RATINGS_MATRIX
from tscscrape.errors import PageWrongFormatError
from tscscrape.utils import timestamp


def scrape_city(city, height_range="All", trim_heightless=True, floor=None):
    """Scrape city data by looking through the page's source and finding javascript tag that declares variable 'buildings' that gets assigned towers data in the form of a javascript object. The extracted object is turned into Python dict and returned.
    """
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
    # get javascript object containg towers' data from page's source
    result = "".join(result.split(keystr)[1:])[:-1]  # trim trailing ';'
    result = json.loads(result)

    if trim_heightless:
        result = [tower for tower in result if tower["height_architecture"] != "-"]

    if floor:
        result = [tower for tower in result if float(tower["height_architecture"]) >= floor]

    return result


def scrape_allcities(height_range="All", trim_heightless=True, floor=None):
    """Scrape all cities data and dump it to JSON files."""
    for i, key in enumerate(key for key in CITIES_CODES.keys() if key != "All"):
        try:
            towers = scrape_city(key, height_range, trim_heightless, floor)
        except PageWrongFormatError:
            towers = []
        if towers:
            data = {
                "timestamp": timestamp(),
                "towers": towers
            }
            destpath = os.path.join(CITIES_PATH, "{}.json".format(key.replace(" ", "_")))
            with open(destpath, mode="w") as jsonfile:
                json.dump(data, jsonfile)
        print("{}: Scraped {} {} for '{}'...".format(
            str(i + 1).zfill(4),
            str(len(towers)),
            "towers" if len(towers) != 1 else "tower",
            key
        ))
        time.sleep(0.02)


def calculate_rating(citydata):
    """Calculate city rating based on city data.

    Tower heights were grouped into tiers using the following formula:

        >>> base = 75.0
        >>> for i in range(6):
        ...     print("{}: {:.0f}".format(i+1, base))
        ...     base *= 1.412
        ...
        1: 75
        2: 106
        3: 150
        4: 211
        5: 298
        6: 421
        >>>

    Point scoring progression inspired by F1 Scoring System
    (https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems)
    """
    def get_tier(towerdata):
        height = float(towerdata["height_architecture"])
        heights = {k: float(v[0]) for k, v in RATINGS_MATRIX.items()}
        if height >= heights["tier_1"] and height < heights["tier_2"]:
            return "tier_1"
        elif height >= heights["tier_2"] and height < heights["tier_3"]:
            return "tier_2"
        elif height >= heights["tier_3"] and height < heights["tier_4"]:
            return "tier_3"
        elif height >= heights["tier_4"] and height < heights["tier_5"]:
            return "tier_4"
        elif height >= heights["tier_5"] and height < heights["tier_6"]:
            return "tier_5"
        elif height >= heights["tier_6"]:
            return "tier_6"
        else:
            raise ValueError("Unexpected height value (lesser than: {}) in parsed data".format(
                int(heights["tier_1"])))

    towers = citydata["towers"]
    counter = Counter()
    for tower in towers:
        tier = get_tier(tower)
        counter[tier] += 1

    scores = {k: v[1] for k, v in RATINGS_MATRIX.items()}

    return sum(v * scores[k] for k, v in counter.items())
