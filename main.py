"""

    Run the script

"""

import os
import json
from pprint import pprint

from tscscrape.scraper import Scraper, City


def main():
    """Run the script"""
    with open("output/cities/Montreal.json") as f:
        data = json.load(f)

    city = City(data)
    print(str(city))
    for tower in city.towers:
        print()
        print(str(tower))


if __name__ == "__main__":
    main()
