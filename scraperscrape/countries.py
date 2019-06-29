"""

    scraperscrape.countries
    ~~~~~~~~~~~~~~~~~~~~~~~~
    Scrape countries metadata from sources other than TSC (it's unavailable in skyscrapers data)

"""

from bs4 import BeautifulSoup, NavigableString

from scraperscrape.utils import readinput

WIKIPEDIA_CA_COUNTRIES = ["Belize", "Costa Rica", "El Salvador",
                          "Guatemala", "Honduras", "Nicaragua", "Panama"]


def _scrape_countries(filename):
    """Scrape country names from locally saved Wikipedia pages.
    """
    def filter_search(tag):
        children = tag.children
        return (tag.name == "td" and tag.has_attr("align") and tag.find("a") and tag.find("span")
        and not any(isinstance(child, NavigableString) for child in children))

    contents = readinput(filename)
    soup = BeautifulSoup(contents, "lxml")
    tds = soup.find_all(filter_search)

    countries = []
    for td in tds:
        element = td.find("a")
        countries.append(element.string)

    return sorted(countries)


def _get_ca_countries():
    """Get names of Central-American countries.
    """
    caribbean = _scrape_countries("caribbean.html")
    ca_countries = [c for c in caribbean if c not in WIKIPEDIA_CA_COUNTRIES]
    ca_countries.extend(WIKIPEDIA_CA_COUNTRIES)
    return sorted(ca_countries)


def get_countries_by_region():
    """Get countries names lists grouped by region (i.e. continent).

    Overlaps:
    ~~~~~~~~~
    Europe-Asia
    ['Armenia', 'Azerbaijan', 'Georgia', 'Kazakhstan', 'Russia', 'Turkey']
    Europe-Africa
    []
    Africa-Asia
    []
    North America-South America
    []
    North America-Central America
    ['Antigua and Barbuda',
    'Bahamas',
    'Barbados',
    'Belize',
    'Costa Rica',
    'Cuba',
    'Dominica',
    'Dominican Republic',
    'El Salvador',
    'Grenada',
    'Guatemala',
    'Haiti',
    'Honduras',
    'Jamaica',
    'Nicaragua',
    'Panama',
    'Saint Kitts and Nevis',
    'Saint Lucia',
    'Saint Vincent and the Grenadines',
    'Trinidad and Tobago']
    South America-Central America
    ['Guyana', 'Suriname']
    Oceania-Asia
    []
    Middle East-Europe
    ['Turkey']
    Middle East-Africa
    []
    Middle East-Asia
    ['Bahrain',
    'Iran',
    'Iraq',
    'Israel',
    'Jordan',
    'Kuwait',
    'Lebanon',
    'Oman',
    'Qatar',
    'Saudi Arabia',
    'Syria',
    'Turkey',
    'United Arab Emirates',
    'Yemen']
    """
    europe = _scrape_countries("europe.html")
    asia = _scrape_countries("asia.html")
    africa = _scrape_countries("africa.html")
    n_america = _scrape_countries("north_america.html")
    s_america = _scrape_countries("south_america.html")
    c_america = _get_ca_countries()
    oceania = _scrape_countries("oceania.html")
    mideast = _scrape_countries("middle_east.html")

    return {
        "EU": sorted([c for c in europe if c not in asia] + ["Russia"]),
        "NA": [c for c in n_america if c not in c_america],
        "CA": [c for c in c_america if c not in s_america] + ["Puerto Rico"],
        "SA": s_america,
        "AF": africa + ["Congo"],
        "ME": mideast,
        "AS": [c for c in asia if c not in mideast and c != "Russia"],
        "OC": oceania
    }


COUNTRYMAP = get_countries_by_region()
