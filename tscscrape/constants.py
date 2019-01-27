"""

    tscscrape.constants
    ~~~~~~~~~~~~~~~~~~~
    Constants to import in other modules

"""

import os
import json
from enum import Enum


class Tier(Enum):
    """A tower's tier"""
    I = 1
    II = 2
    III = 3
    IV = 4
    V = 5
    VI = 6


# parse application settings from "settings/settings.json"
with open(os.path.join("settings", "settings.json"), encoding="utf-8") as f:
    _settings = json.load(f)

URL = _settings["url"]
INPUT_PATH = os.path.join(*_settings["input_path"])
OUTPUT_JSON_PATH = os.path.join(*_settings["output_json_path"])
OUTPUT_TXT_PATH = os.path.join(*_settings["output_txt_path"])
# change rating matrix's keys to Tier enums
RATINGS_MATRIX = {tier: tuple(item[1]) for tier, item
                  in zip(Tier, sorted(_settings["ratings_matrix"].items(),
                                      key=lambda pair: pair[0]))}
STATUSMAP = _settings["status"]
REGIONMAP = _settings["regions"]
