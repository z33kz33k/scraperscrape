"""

    Run the script

"""

import os
import json
from pprint import pprint

from tscscrape.scraper import getcities
from tscscrape.output import (print_city, print_country, print_region, print_world, regions_totxt,
                              countries_totxt, cities_totxt)


def main():
    """Run the script"""
    cities_totxt()


if __name__ == "__main__":
    main()
