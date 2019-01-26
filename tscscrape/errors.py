"""

    tscscrape.errors
    ~~~~~~~~~~~~~~~~~
    Custom errors for better clarity

"""


class PageWrongFormatError(ValueError):
    """Raised when the page cannot be parsed due to wrong format"""
