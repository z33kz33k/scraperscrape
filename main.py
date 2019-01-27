"""

    Run the script

"""

import os
import json
from pprint import pprint

from tscscrape.scraper import getcities
from tscscrape.debug import print_city, print_country, print_region


def main():
    """Run the script"""
    # print_region("Africa")
    print_country("Poland", verbose=True)
    # print_city("Warsaw")


if __name__ == "__main__":
    main()
