"""

    scraperscrape.utils
    ~~~~~~~~~~~~~~~
    Auxiliary functions

"""

import datetime as dt
import json
import os
from bs4 import BeautifulSoup

from scraperscrape.constants import INPUT_PATH, OUTPUT_JSON_PATH


def timestamp(underscores=False):
    """Return timestamp of now"""
    return "{:%Y%m%d_%H_%M_%S}".format(
        dt.datetime.now()) if underscores else "{:%Y-%b-%d %H:%M:%S}".format(dt.datetime.now())


def split_json(src, dest):
    """Split large JSON file into smaller ones"""
    with open(src) as srcfile:
        data = json.load(srcfile)
        tempdata = data.get("data")
        data = tempdata if tempdata is not None else data

    for k, v in data.items():
        destpath = os.path.join(dest, "{}.json".format(k.replace(" ", "_")))
        with open(destpath, mode="w") as destfile:
            json.dump({"timestamp": timestamp(), "towers": v}, destfile, sort_keys=True, indent=4)


def readinput(filename):
    """Read input file contents and return it as one '\\n' separated string

    Arguments:
        filename {str} -- name of the file to be read
    """
    path = os.path.join(INPUT_PATH, filename)
    with open(path) as file:
        contents = "\n".join(file.readlines())
    return contents


def asteriskify(text, count=3):
    """Decorate text with asterisks

    Arguments:
        text {str} -- a text to be decorated
        count {int} -- number of asterisks (default: {3})

    Returns:
        str -- a decorated text
    """
    decor = "*" * count
    return "{} {} {}".format(decor, text, decor)


def rightjustify(linetext, linecount, max_countwidth):
    """Justify ordered line to the right

    Arguments:
        linetext {str} -- a text to justify
        linecount {int} -- a line count (1-based)
        max_countwidth {int} -- a maximum count width

    Returns:
        str -- a justified line
    """
    fill_length = max_countwidth - len(str(linecount)) + 1
    return "{}.{}{}".format(linecount, " " * fill_length,  linetext)


def extract_tower_properties():
    """Extract all tower properties as scraped and saved in JSON files

    Returns:
        list -- a list of tower properties
    """
    properties = []
    for root, _, files in os.walk(OUTPUT_JSON_PATH):
        for file in files:
            path = os.path.join(root, file)
            with open(path) as f:
                data = json.load(f)

            properties.extend(k for tower in data["towers"] for k in tower if k not in properties)

    return sorted(properties)
