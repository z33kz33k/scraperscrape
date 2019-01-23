"""

    tscscrape.utils
    ~~~~~~~~~~~~~~~
    Auxiliary functions

"""

import datetime
import json
import os
from bs4 import BeautifulSoup

from tscscrape.constants import INPUT_PATH


def timestamp():
    """Return timestamp of now."""
    return "{:%Y-%b-%d %H:%M:%S}".format(datetime.datetime.now())


def split_json(src, dest):
    """Split large JSON file into smaller ones."""
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
