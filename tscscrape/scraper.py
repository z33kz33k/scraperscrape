"""

    tscscrape.scraper
    ~~~~~~~~~~~~~~~~~
    Scrape the scrapers

"""

import requests
from bs4 import BeautifulSoup
import json
import time
import os
from collections import Counter
import itertools
import csv
from pprint import pprint

from tscscrape.constants import URL, CITIES, HEIGHT_RANGES
from tscscrape.constants import CITIES_PATH, RATINGS_MATRIX, STATUS
from tscscrape.errors import PageWrongFormatError
from tscscrape.utils import timestamp


class Scraper:
    """Scrapes data from www.skyscrapercenter.com"""

    HOOK = "var buildings = "

    def __init__(self, height_range="All", trim_heightless=True, height_floor=75):
        """
        Keyword Arguments:
            height_range {str} -- height range options from the website's GUI: 'All', 'Under 100m', '150m+', '200m+', '250m+', '300m+', '350m+', '400m+', '450m+' and '500m+' (default: {"All"})
            trim_heightless {bool} -- decides if records with no height should be trimmed (default: {True})
            height_floor {int} -- minimum tower's height for scrapin (default: {75})
        """
        self.height_range = height_range
        self.trim_heightless = trim_heightless
        self.height_floor = height_floor

    def scrape_city(self, city):
        """Scrape city towers data by looking through the page's source and finding javascript tag that declares variable 'buildings' that gets towers data in the form of a javascript object assigned. The extracted object is turned into Python dict and returned

        Arguments:
            city {str} -- name of the city to scrape chosen from options available in the website GUI

        Raises:
            PageWrongFormatError -- raised when page can't be scraped due to a wrong format

        Returns:
            dict -- scraped towers data
        """
        url = URL.format(CITIES[city], HEIGHT_RANGES[self.height_range])
        contents = requests.get(url).text
        soup = BeautifulSoup(contents, "lxml")
        try:
            script_tag = next(tag for tag in soup.find_all("script", type="text/javascript")
                              if self.HOOK in tag.text)
        except StopIteration:
            raise PageWrongFormatError(
                "Page for '{}' seems to have wrong format (missing '{}' string).\nFull URL: {}".format(city, self.HOOK, url))
        # get javascript object containg towers' data from page's source
        result = script_tag.text.strip()
        result = "".join(result.split(self.HOOK)[1:])[:-1]  # trim trailing ';'
        result = json.loads(result)

        if self.trim_heightless:
            result = [tower for tower in result if tower["height_architecture"] != "-"]

        if self.height_floor:
            result = [tower for tower in result if float(tower["height_architecture"])
                      >= self.height_floor]

        return result

    def scrape_allcities(self, start=None, end=None):
        """Scrape all cities data and dump it to JSON files. Optionally define a range to scrape

        Keyword Arguments:
            start {int} -- start of optional range (default: {None})
            end {int} -- end of optional range (default: {None})
        """
        start = start if start is not None else 0
        end = end if end is not None else len(CITIES) - 1

        cities = (city for city in CITIES.keys() if city != "All")
        for i, city in enumerate(itertools.islice(cities, start, end)):
            try:
                towers = self.scrape_city(city)
            except PageWrongFormatError:
                towers = []
            if towers:
                data = {
                    "timestamp": timestamp(),
                    "towers": towers
                }
                destpath = os.path.join(CITIES_PATH, "{}.json".format(city.replace(" ", "_")))
                with open(destpath, mode="w") as jsonfile:
                    json.dump(data, jsonfile, sort_keys=True, indent=4)
            print("{}: Scraped {} {} for '{}'...".format(
                str(i + start + 1).zfill(4),
                str(len(towers)),
                "towers" if len(towers) != 1 else "tower",
                city
            ))
            time.sleep(0.02)


def get_tiers(citydata):
    """Group towers into tiers based on their height"""

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
    tiers = Counter()
    for tower in towers:
        tier = get_tier(tower)
        tiers[tier] += 1

    return tiers


def calculate_rating(tiers):
    """Calculate city rating according to height tiers of its towers.

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
    scores = {k: v[1] for k, v in RATINGS_MATRIX.items()}
    return sum(v * scores[k] for k, v in tiers.items())


def get_uncompleted(citydata):
    """Get number of uncompleted towers"""
    towers = citydata["towers"]
    uncompleted = [tower for tower in towers if tower["status"] != STATUS["Completed"]]
    return len(uncompleted)


# TODO: implement City class and use it to generate output data
