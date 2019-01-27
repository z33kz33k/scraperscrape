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

from tscscrape.constants import URL, CITIES_PATH, RATINGS_MATRIX, STATUSMAP, REGIONMAP, Tier
from tscscrape.errors import (PageWrongFormatError, InvalidCityError,
                              InvalidCountryError, InvalidRegionError)
from tscscrape.utils import timestamp, readinput, asteriskify
from tscscrape.countries import COUNTRYMAP


SUBCITYMAP = {
    "Courbevoie": "Paris",
    "Puteaux": "Paris",
    "Courbevoie": "Paris",
    "Nanterre": "Paris",
    "Bagnolet": "Paris",
    "Issy-les-Moulineaux": "Paris",
    "Aubervilliers": "Paris",
    "Saint Denis": "Paris",
    "L'Hospitalet de Llobregat": "Barcelona",
    "Rijswijk": "The Hague",
    "Herlev": "Copenhagen",
    "Oeiras": "Lisbon"
}


def scrape_citycodes():
    """Scrape city codes to be entered in URL

    Returns:
        dict -- city code map
    """
    contents = readinput("default.html")
    soup = BeautifulSoup(contents, "lxml")
    result = soup.find("select", id="base_city")
    result = result.find_all("option")
    return {tag.string: tag["value"] for tag in result}


def scrape_heightranges():
    """Scrape codes of height ranges to be entered in URL

    Returns:
        dict -- height range code map
    """
    contents = readinput("default.html")
    soup = BeautifulSoup(contents, "lxml")
    result = soup.find("select", id="base_height_range")
    result = result.find_all("option")
    return {tag.string: tag["value"] for tag in result}


class Scraper:
    """Scrapes data from www.skyscrapercenter.com"""

    HOOK = "var buildings = "
    # keys of below dicts are the same as options in "Base Data Range" form on the website
    CITYCODE_MAP = scrape_citycodes()
    HEIGHTRANGE_MAP = scrape_heightranges()

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
            PageWrongFormatError -- when page can't be scraped due to a wrong format

        Returns:
            dict -- scraped towers data
        """
        url = URL.format(self.CITYCODE_MAP[city], self.HEIGHTRANGE_MAP[self.height_range])
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
        end = end if end is not None else len(self.CITYCODE_MAP) - 1

        cities = (city for city in self.CITYCODE_MAP.keys() if city != "All")
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
        return "{}, {:.0f}m".format(self.name, self.height)

    def _parse_attribute(self, key):
        """Parse attribute

        Arguments:
            key {str} -- key for scraped data dict

        Returns:
            str / int / float / None -- parsed attribute or 'None'
        """
        try:
            attribute = self.data[key] if self.data[key] not in ("-", "") else None
        except KeyError:
            attribute = None
        return attribute

    def getdescription(self):
        """Get description listing main properties of this tower

        Returns:
            str -- a description
        """
        desc = ""
        if self.name:
            desc += "{}\n".format(asteriskify(self.name))
        if self.height:
            desc += f"Height: {self.height}\n"
        if self.floors:
            desc += f"Floors: {self.floors}\n"
        if self.status:
            desc += f"Status: {STATUSMAP[self.status]}\n"
        if self.start:
            desc += f"Started: {self.start}\n"
        if self.completed:
            desc += f"Completed: {self.completed}\n"
        if self.functions:
            desc += f"Functions: {self.functions}\n"
        if self.rank:
            desc += f"Rank: {self.rank}\n"

        return desc[:-1] if desc[-1] == "\n" else desc


def get_tiers(towers):
    """Group towers into tiers based on their height and count them

    Arguments:
        towers {list} -- a list of Tower objects

    Raises:
        ValueError -- when height out of expected range is encountered

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
        """Get tier designation

        Arguments:
            tower {tscscrape.scraper.Tower} -- a tower

        Raises:
            ValueError -- when unexpected height value is encountered

        Returns:
            str -- a tier designation
        """
        heightmap = {k: v[0] for k, v in RATINGS_MATRIX.items()}
        if tower.height >= heightmap[Tier.I] and tower.height < heightmap[Tier.II]:
            return Tier.I
        elif tower.height >= heightmap[Tier.II] and tower.height < heightmap[Tier.III]:
            return Tier.II
        elif tower.height >= heightmap[Tier.III] and tower.height < heightmap[Tier.IV]:
            return Tier.III
        elif tower.height >= heightmap[Tier.IV] and tower.height < heightmap[Tier.V]:
            return Tier.IV
        elif tower.height >= heightmap[Tier.V] and tower.height < heightmap[Tier.VI]:
            return Tier.V
        elif tower.height >= heightmap[Tier.VI]:
            return Tier.VI
        else:
            raise ValueError("Unexpected height value (lesser than: {}) in parsed data".format(
                int(heightmap[Tier.I])))

    tiers = Counter()
    for tower in towers:
        tier = get_tier(tower)
        tiers[tier] += 1
    return tiers


def calculate_rating(towers):
    """Calculate city rating according to height tiers of selected towers.

    Arguments:
        towers {list} -- a list of Tower objects

    Returns:
        int -- calculated rating

    Tiers' point scoring progression inspired by F1 Scoring System(https://en.wikipedia.org/wiki/List_of_Formula_One_World_Championship_points_scoring_systems)
    """
    scoremap = {k: v[1] for k, v in RATINGS_MATRIX.items()}
    return sum(count * scoremap[tier] for tier, count in get_tiers(towers).items())


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
        self.country = self._getcountry()
        self.region = self._getregion()
        self.towers = [Tower(towerdata) for towerdata in data["towers"]]
        self.completed = [tower for tower in self.towers if tower.status == "COM"]
        self.arch_toppedout = [tower for tower in self.towers if tower.status == "UCT"]
        self.struct_toppedout = [tower for tower in self.towers if tower.status == "STO"]
        self.under_construction = [tower for tower in self.towers if tower.status == "UC"]
        self.rating = calculate_rating(self.towers)
        self.uncompleted = self.getuncompleted()  # percentage (float)
        self.parentcity_name = SUBCITYMAP.get(self.name)  # 'None' if there's no parent city

    def __str__(self):
        return "{} ({})".format(self.name, self.rating)

    def _getcountry(self):
        """Get city's country

        Returns:
            str -- country
        """
        country = self.data["towers"][0].get("country_slug").title().replace("-", " ")
        if country == "Lao Peoples Democratic Republic":
            country = "Laos"
        return country

    def _getregion(self):
        """Get city's region/continent

        Returns:
            str -- region/continent
        """
        # TODO: adjust region of cities that are located in countries spanning more than one
        # region (cases like Vladivostok being considered as an European city)
        try:
            region_code, _ = next((region_code, country) for region_code, countries in
                                  COUNTRYMAP.items() for country in countries if country.casefold() == self.country.casefold())
        except StopIteration:
            return None

        return REGIONMAP[region_code]

    def getdescription(self):
        """Get description listing main properties of this city

        Returns:
            str -- a description
        """
        desc = f"*** {self.name} ***\n"
        desc += f"Country: {self.country}\n"
        desc += f"Region: {self.region}\n"
        desc += "{} {}: {}\n".format(
            len(self.towers),
            "tower" if len(self.towers) == 1 else "towers",
            ", ".join([tower.name for tower in self.towers])
        )
        desc += "Tiers: {}\n".format(", ".join(["{}: {}".format(tier.name, count)
                                                for tier, count
                                                in sorted(get_tiers(self.towers).items(),
                                                          key=lambda item: item[0].value)]))
        desc += "Rating: {}{}\n".format(
            self.rating,
            f" ({self.uncompleted:.1f}% uncompleted)" if self.uncompleted else ""
        )
        desc += f"Scraped on: {self.timestamp}"
        return desc

    def getuncompleted(self):
        """Get percentage of total rating for uncompleted towers in this city

        Returns:
            float -- percentage of rating for uncompleted towers
        """
        uc_rating = calculate_rating([*self.arch_toppedout, *self.struct_toppedout,
                                      *self.under_construction])
        return uc_rating * 100 / self.rating


def getcities(merge_subcities=True, region_filter=None, country_filter=None):
    """Get cities from scraped data

    Keyword Arguments:
        merge_subcities {bool} -- flag to merge or not subsidiary cities into their parent (default: {True})
        region_filter {str} -- a name of a region to narrow the output to (default: {None})
        country_filter {str} -- a name of a country to narrow the output to (default: {None})

    Raises:
        InvalidRegionError -- when invalid region filter is provided
        InvalidCountryError -- when invalid country filter is provided

    Returns:
        list -- a list of City objects
    """
    cities = []
    for root, _, files in os.walk(CITIES_PATH):
        for file in files:
            path = os.path.join(root, file)
            with open(path) as f:
                data = json.load(f)
            cities.append(City(data))

    if merge_subcities:
        subcities = [city for city in cities if city.parentcity_name]
        # merge subsidiary cities into their parents
        for parentcity in [city for city in cities if city.name in set(SUBCITYMAP.values())]:
            mergecities(parentcity,
                        *[sc for sc in subcities if sc.parentcity_name == parentcity.name])
        # filter out subsidiaries from the output
        cities = [city for city in cities if city not in subcities]

    if region_filter:
        cities = [city for city in cities if city.region == region_filter]
        if not cities:
            raise InvalidRegionError(f"Invalid region filter provided: {region_filter}")
    if country_filter:
        cities = [city for city in cities if city.country == country_filter]
        if not cities:
            raise InvalidCountryError(f"Invalid country filter provided: {country_filter}")

    return sorted(cities, key=lambda c: (c.rating, c.name), reverse=True)


def getcity(city):
    """Get city from scraped data

    Arguments:
        city {str} -- a name of the city

    Raises:
        InvalidCountryError -- when invalid country name is provided

    Returns:
        tscscrape.scraper.City -- a city
    """
    path = os.path.join(CITIES_PATH, "{}{}".format(city.replace(" ", "_"), ".json"))
    try:
        with open(path) as f:
            data = json.load(f)
    except IOError:
        raise InvalidCityError(f"Invalid city name provided: {city}")

    return City(data)


def mergecities(parentcity, *subcities):
    """Merge subsidiary subcities into the parent city

    Arguments:
        parentcity {tscscrape.scraper.City} -- parent city
        subcities {list} -- variable number of subsidiary cities packed into list

    Returns:
        tscscrape.scraper.City -- the parent city with merged subsidiaries
    """
    towers = [tower for subcity in subcities for tower in subcity.towers]
    # extending parentcity
    parentcity.towers.extend(towers)
    parentcity.completed = [tower for tower in parentcity.towers if tower.status == "COM"]
    parentcity.arch_toppedout = [tower for tower in parentcity.towers if tower.status == "UCT"]
    parentcity.struct_toppedout = [tower for tower in parentcity.towers if tower.status == "STO"]
    parentcity.under_construction = [tower for tower in parentcity.towers if tower.status == "UC"]
    parentcity.rating = calculate_rating(parentcity.towers)
    parentcity.uncompleted = parentcity.getuncompleted()  # percentage (float)

    return parentcity


class Country:
    """A country with skyscraper cities"""

    def __init__(self, name, cities):
        """
        Arguments:
            name {str} -- a name for this country
            cities {list} -- a list of City objects
        """
        self.name = name
        self.cities = cities
        self.region = cities[0].region
        self.towers = [tower for city in self.cities for tower in city.towers]
        self.completed = [tower for city in self.cities for tower in city.completed]
        self.arch_toppedout = [tower for city in self.cities for tower in city.arch_toppedout]
        self.struct_toppedout = [tower for city in self.cities for tower in city.struct_toppedout]
        self.under_construction = [tower for city in self.cities for tower
                                   in city.under_construction]
        self.rating = sum(city.rating for city in self.cities)
        self.uncompleted = self.getuncompleted()  # percentage (float)

    def __str__(self):
        return "{} ({})".format(self.name, self.rating)

    def getdescription(self):
        """Get description listing main properties of this country

        Returns:
            str -- a description
        """
        desc = "{}\n".format(asteriskify(self.name))
        desc += f"Region: {self.region}\n"
        desc += "{} {}: {}\n".format(
            len(self.cities),
            "city" if len(self.cities) == 1 else "cities",
            ", ".join([city.name for city in self.cities])
        )
        desc += "Tiers: {}\n".format(", ".join(["{}: {}".format(tier.name, count)
                                                for tier, count
                                                in sorted(get_tiers(self.towers).items(),
                                                          key=lambda item: item[0].value)]))
        desc += "Rating: {}{}".format(
            self.rating,
            f" ({self.uncompleted:.1f}% uncompleted)" if self.uncompleted else ""
        )
        return desc

    def getuncompleted(self):
        """Get percentage of total rating for uncompleted towers in this city

        Returns:
            float -- percentage of rating for uncompleted towers
        """
        uc_rating = calculate_rating([*self.arch_toppedout, *self.struct_toppedout,
                                      *self.under_construction])
        return uc_rating * 100 / self.rating


class Region(Country):
    """A region with skyscraper cities"""

    def __init__(self, name, cities):
        """
        Arguments:
            name {str} -- a name for this region
            cities {list} -- a list of City objects
        """
        super().__init__(name, cities)
        del self.region
        self.countries = self._getcountries()

    def __str__(self):
        return "{} ({})".format(self.name, self.rating)

    def _getcountries(self):
        try:
            countrynames = next(COUNTRYMAP[region_code] for region_code, region
                                in REGIONMAP.items() if region == self.name)
        except StopIteration:
            raise InvalidRegionError(f"Invalid region name provided: {self.name}")

        return sorted([Country(name, [city for city in self.cities if city.country == name])
                       for name in countrynames if name
                       in set(city.country for city in self.cities)],
                      key=lambda c: c.rating, reverse=True)

    def getdescription(self):
        """Get description listing main properties of this country

        Returns:
            str -- a description
        """
        desc = "{}\n".format(asteriskify(self.name))
        desc += "{} {}: {}\n".format(
            len(self.countries),
            "country" if len(self.countries) == 1 else "countries",
            ", ".join([country.name for country in self.countries])
        )
        desc += "Tiers: {}\n".format(", ".join(["{}: {}".format(tier.name, count)
                                                for tier, count
                                                in sorted(get_tiers(self.towers).items(),
                                                          key=lambda item: item[0].value)]))
        desc += "Rating: {}{}".format(
            self.rating,
            f" ({self.uncompleted:.1f}% uncompleted)" if self.uncompleted else ""
        )
        return desc
