"""

    scraperscrape.errors
    ~~~~~~~~~~~~~~~~~
    Custom errors for better clarity

"""


class PageWrongFormatError(ValueError):
    """Raised when the page cannot be parsed due to wrong format"""


class InvalidCityError(ValueError):
    """Raised when the an invalid city name was provided as input"""


class InvalidCountryError(ValueError):
    """Raised when the an invalid country name was provided as input"""


class InvalidRegionError(ValueError):
    """Raised when the an invalid region name was provided as input"""
