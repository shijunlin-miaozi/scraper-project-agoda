# agoda/utilities/headers/referers.py

"""
Referer generation and Accept-Language localization based on city/country mapping.
"""

import re
import random

# City-to-country and language mappings
CITY_TO_COUNTRY = {
    "paris": "FR", "rome": "IT", "berlin": "DE", "madrid": "ES", "lisbon": "PT",
    "vienna": "AT", "prague": "CZ", "budapest": "HU", "warsaw": "PL", "amsterdam": "NL",
    "stockholm": "SE", "oslo": "NO", "helsinki": "FI", "copenhagen": "DK", "sofia": "BG",
    "bucharest": "RO", "brussels": "BE", "athens": "GR", "zagreb": "HR", "ljubljana": "SI"
}

COUNTRY_LANGUAGE_MAP = {
    "FR": "fr-FR", "DE": "de-DE", "IT": "it-IT", "ES": "es-ES", "PT": "pt-PT",
    "AT": "de-AT", "CZ": "cs-CZ", "HU": "hu-HU", "PL": "pl-PL", "NL": "nl-NL",
    "SE": "sv-SE", "NO": "no-NO", "FI": "fi-FI", "DK": "da-DK", "BG": "bg-BG",
    "RO": "ro-RO", "BE": "fr-BE", "GR": "el-GR", "HR": "hr-HR", "SI": "sl-SI"
}

COUNTRY_GOOGLE_DOMAIN = {
    "FR": "google.fr", "DE": "google.de", "IT": "google.it", "ES": "google.es", "PT": "google.pt",
    "AT": "google.at", "CZ": "google.cz", "HU": "google.hu", "PL": "google.pl", "NL": "google.nl",
    "SE": "google.se", "NO": "google.no", "FI": "google.fi", "DK": "google.dk", "BG": "google.bg",
    "RO": "google.ro", "BE": "google.be", "GR": "google.gr", "HR": "google.hr", "SI": "google.si"
}

COUNTRY_AGODA_PATH = {
    "FR": "fr-fr", "DE": "de-de", "IT": "it-it", "ES": "es-es", "PT": "pt-pt",
    "AT": "de-at", "CZ": "cs-cz", "HU": "hu-hu", "PL": "pl-pl", "NL": "nl-nl",
    "SE": "sv-se", "NO": "no-no", "FI": "fi-fi", "DK": "da-dk", "BG": "bg-bg",
    "RO": "ro-ro", "BE": "fr-be", "GR": "el-gr", "HR": "hr-hr", "SI": "sl-si"
}


def generate_referer_pool(city_list, ratio_google=0.4, ratio_agoda=0.5, ratio_misc=0.1):
    google_refs = []
    agoda_refs = []
    language_map = {}

    for city in city_list:
        city_key = city.lower()
        country = CITY_TO_COUNTRY.get(city_key)
        domain = COUNTRY_GOOGLE_DOMAIN.get(country, "google.com")
        path = COUNTRY_AGODA_PATH.get(country)
        google_refs.append(f"https://www.{domain}/search?q=best+hotels+in+{city.replace(' ', '+')}")
        if path:
            agoda_refs.append(f"https://www.agoda.com/{path}/search")
        language_map[city_key] = COUNTRY_LANGUAGE_MAP.get(country, "en-US")

    misc_refs = [
        "https://www.bing.com/search?q=hotels+in+tokyo",
        "https://duckduckgo.com/?q=agoda+paris+hotel",
    ]

    pool = (
        random.choices(google_refs, k=int(ratio_google * 100)) +
        random.choices(agoda_refs, k=int(ratio_agoda * 100)) +
        random.choices(misc_refs, k=int(ratio_misc * 100))
    )

    return pool, language_map

def load_city_names_from_urls(hotel_urls):
    city_pattern = re.compile(r"/hotel/([\w\-]+)-[a-z]{2}\.html$")
    city_names = set()
    for url in hotel_urls:
        match = city_pattern.search(url)
        if match:
            city = match.group(1).replace('-', ' ')
            city_names.add(city.lower())
    return list(city_names)
