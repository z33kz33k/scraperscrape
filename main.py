"""

    Run the script

"""

import os
import json
from pprint import pprint

from tscscrape.scraper import getcities


def main():
    """Run the script"""
    pprint(sorted([(city.name, city.country, city.rating) for city
                   in getcities() if city.region == "Europe"],
                  key=lambda pair: pair[2], reverse=True))


if __name__ == "__main__":
    main()
