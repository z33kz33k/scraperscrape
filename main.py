"""

    Run the script

"""

import os
import json
from pprint import pprint

from tscscrape.scraper import getcities
from tscscrape.debug import print_city, print_country, print_region, print_world


def main():
    """Run the script"""
    # print_region("Middle East")
    # print_country("Poland")
    # print_city("Warsaw")
    print_world(verbose=True)


if __name__ == "__main__":
    main()
