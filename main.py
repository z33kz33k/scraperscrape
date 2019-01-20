import os

from tscscrape.scraper import scrape_allcities
from tscscrape.utils import split_json


def main():
    """Run the script"""
    # scrape_allcities(floor=75)
    src = os.path.join("output", "cities.json")
    dest = os.path.join("output", "cities")
    split_json(src, dest)


if __name__ == "__main__":
    main()
