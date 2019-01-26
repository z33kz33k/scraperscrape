"""

    tscscrape.constants
    ~~~~~~~~~~~~~~~~~~~
    Constants to import in other modules

"""

import os
import json

# parse application settings from "settings/settings.json"
with open(os.path.join("settings", "settings.json"), encoding="utf-8") as f:
    _settings = json.load(f)

URL = _settings["url"]
CITIES_PATH = os.path.join(*_settings["cities_path"])
INPUT_PATH = os.path.join(*_settings["input_path"])
RATINGS_MATRIX = _settings["ratings_matrix"]
STATUSMAP = _settings["status"]
REGIONMAP = _settings["regions"]
