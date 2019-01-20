"""

    Run the script

"""

import os
import json
from pprint import pprint

from tscscrape.scraper import scrape_allcities, calculate_rating
from tscscrape.utils import split_json
from tscscrape.constants import CITIES_PATH
from tscscrape.regions import scrape_countries, get_ca_countries


def main():
    """Run the script"""
    pprint(scrape_countries("caribbean.html"))


if __name__ == "__main__":
    main()
