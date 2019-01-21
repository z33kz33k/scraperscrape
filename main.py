"""

    Run the script

"""

import os
import json
from pprint import pprint

from tscscrape.scraper import Scraper, calculate_rating
from tscscrape.utils import split_json
from tscscrape.constants import CITIES_PATH
from tscscrape.regions import get_countries_by_region


def main():
    """Run the script"""
    scraper = Scraper()
    scraper.scrape_allcities(250, 265)


if __name__ == "__main__":
    main()
