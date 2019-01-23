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
import codecs
import csv
from pprint import pprint

from tscscrape.constants import URL, CITIES_PATH, RATINGS_MATRIX, STATUS, REGIONS
from tscscrape.errors import PageWrongFormatError
from tscscrape.utils import timestamp, readinput
from tscscrape.countries import COUNTRIES


def scrape_citiescodes():
    """Scrape city codes to be entered in URL."""
    contents = readinput("default.html")
    soup = BeautifulSoup(contents, "lxml")
    result = soup.find("select", id="base_city")
    result = result.find_all("option")
    return {tag.string: tag["value"] for tag in result}


def scrape_heightranges():
    """Scrape codes of height ranges to be entered in URL."""
    contents = readinput("default.html")
    soup = BeautifulSoup(contents, "lxml")
    result = soup.find("select", id="base_height_range")
    result = result.find_all("option")
    return {tag.string: tag["value"] for tag in result}


class Scraper:
    """Scrapes data from www.skyscrapercenter.com"""

    HOOK = "var buildings = "
    # keys of below dicts are the same as options in "Base Data Range" form on the website
    CITIES = scrape_citiescodes()
    HEIGHT_RANGES = scrape_heightranges()

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
        url = URL.format(self.CITIES[city], self.HEIGHT_RANGES[self.height_range])
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
            result = [tower for tower in result if tower["height_architecture"] not in ("-", "")]

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
        end = end if end is not None else len(self.CITIES) - 1

        cities = (city for city in self.CITIES.keys() if city != "All")
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


class Tower:
    """A skyscraper scraped"""

    def __init__(self, data):
        """
        Arguments:
            data {dict} -- scraped tower data
        """
        self.data = data
        self.id_ = self._parse_attribute("id")
        self.name = self._parse_attribute("name")
        self.height = self._parse_attribute("height_architecture")
        self.floors = self._parse_attribute("floors_above")
        self.status = self._parse_attribute("status")
        self.start = self._parse_attribute("start")
        self.completed = self._parse_attribute("completed")
        self.functions = self._parse_attribute("functions")
        self.rank = self._parse_attribute("rank")
        self.latitude = self._parse_attribute("latitude")
        self.longitude = self._parse_attribute("longitude")

    def __str__(self):
        result = ""
        if self.name:
            result += f"*** {self.name} ***\n"
        if self.height:
            result += f"Height: {self.height}\n"
        if self.floors:
            result += f"Floors: {self.floors}\n"
        if self.status:
            result += f"Status: {STATUS[self.status]}\n"
        if self.start:
            result += f"Started: {self.start}\n"
        if self.completed:
            result += f"Completed: {self.completed}\n"
        if self.functions:
            result += f"Functions: {self.functions}\n"
        if self.rank:
            result += f"Rank: {self.rank}\n"

        return result[:-1] if result[-1] == "\n" else result

    def _parse_attribute(self, key):
        try:
            attribute = self.data[key] if self.data[key] not in ("-", "") else None
        except KeyError:
            attribute = None
        return attribute


class City:
    """A city with skyscrapers in it"""

    def __init__(self, data):
        """
        Arguments:
            data {dict} -- scraped city data
        """
        self.data = data
        self.timestamp = data["timestamp"]
        self.name = data["towers"][0].get("city")
        self.country = data["towers"][0].get("country_slug").title().replace("-", " ")
        self.region = self._getregion()
        self.towers = [Tower(towerdata) for towerdata in data["towers"]]
        self.completed = [tower for tower in self.towers if tower.status == "COM"]
        self.arch_toppedout = [tower for tower in self.towers if tower.status == "UCT"]
        self.struct_toppedout = [tower for tower in self.towers if tower.status == "STO"]
        self.under_construction = [tower for tower in self.towers if tower.status == "UC"]
        self.rating = self.calculate_rating(self.towers)
        self.uncompleted = self.getuncompleted()  # percentage (float)

    def __str__(self):
        tiersmap = {k: v for k, v in zip(sorted(RATINGS_MATRIX.keys()),
                                         ["I", "II", "III", "IV", "V", "VI"])}
        result = f"*** {self.name} ***\n"
        result += f"Country: {self.country}\n"
        result += f"Region: {self.region}\n"
        result += "{} towers: {}\n".format(len(self.towers),
                                           ", ".join([tower.name for tower in self.towers]))
        result += "Tiers: {}\n".format(", ".join(["{}: {}".format(tiersmap[k], v)
                                                  for k, v in sorted(self.get_tiers(self.towers).items(), key=lambda args: args[0])]))
        result += "Rating: {}{}\n".format(
            self.rating,
            f" ({self.uncompleted:.1f}% uncompleted)" if self.uncompleted else ""
        )
        result += f"Scraped on: {self.timestamp}"
        return result

    def _getregion(self):
        """Get city's region/continent

        Returns:
            str -- region/continent
        """
        try:
            region_code, _ = next((region_code, country) for region_code, countries in
                                  COUNTRIES.items() for country in countries if country.casefold() == self.country.casefold())
        except StopIteration:
            return None

        return REGIONS[region_code]

    def get_tiers(self, towers):
        """Group towers into tiers based on their height

        Raises:
            ValueError -- raised when height out of expected range is encountered

        Returns:
            collections.Counter -- {tier: number of towers}

        Tower heights are grouped into tiers using the following formula:

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
        """

        def get_tier(tower):
            heights = {k: v[0] for k, v in RATINGS_MATRIX.items()}
            if tower.height >= heights["tier_1"] and tower.height < heights["tier_2"]:
                return "tier_1"
            elif tower.height >= heights["tier_2"] and tower.height < heights["tier_3"]:
                return "tier_2"
            elif tower.height >= heights["tier_3"] and tower.height < heights["tier_4"]:
                return "tier_3"
            elif tower.height >= heights["tier_4"] and tower.height < heights["tier_5"]:
                return "tier_4"
            elif tower.height >= heights["tier_5"] and tower.height < heights["tier_6"]:
                return "tier_5"
            elif tower.height >= heights["tier_6"]:
                return "tier_6"
            else:
                raise ValueError("Unexpected height value (lesser than: {}) in parsed data".format(
                    int(heights["tier_1"])))

        tiers = Counter()
        for tower in towers:
            tier = get_tier(tower)
            tiers[tier] += 1

        return tiers

    def calculate_rating(self, towers):
        """Calculate city rating according to height tiers of selected towers.

        Returns:
            int -- calculated rating

        Tiers' point scoring progression inspired by F1 Scoring System(https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems)
        """
        scores = {k: v[1] for k, v in RATINGS_MATRIX.items()}
        return sum(v * scores[k] for k, v in self.get_tiers(towers).items())

    def getuncompleted(self):
        """Get percentage (float) of total rating for uncompleted towers in this city

        Returns:
            float -- percentage of rating for uncompleted towers

        """
        ucrating = self.calculate_rating([*self.arch_toppedout, *self.struct_toppedout,
                                          *self.under_construction])
        return ucrating * 100 / self.rating
