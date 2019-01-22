"""

    Run the script

"""

import os
import json
from pprint import pprint

from tscscrape.scraper import Scraper, City


def main():
    """Run the script"""
    with open("output/cities/London.json") as f:
        data = json.load(f)

    city = City(data)
    print(str(city))


if __name__ == "__main__":
    main()
