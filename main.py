"""

    Run the script

"""

import os
import json
from pprint import pprint

from scraperscrape.scraper import getcities, Scraper
from scraperscrape.output import (print_city, print_country, print_region, print_world,
regions_totxt, countries_totxt, cities_totxt, world_totxt)
from scraperscrape.utils import extract_tower_properties


def main():
    """Run the script"""
    # for p in extract_tower_properties():
    #     print(p)
    s = Scraper()
    s.scrape_alltowers(start=500, end=505)


if __name__ == "__main__":
    main()
