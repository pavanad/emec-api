# -*- coding: utf-8 -*-

from unicodedata import normalize


def normalize_key(key: str) -> str:
    """Format the key to be used in json.

    Args:
        key (str): Field collected in MEC data scraping.

    Returns:
        str: Returns the formatted string to be used in the json.
    """
    aux = key.strip(" :").replace(" ", "_").lower()
    aux = aux.replace("_-_sigla", "")

    return normalize("NFKD", aux).encode("ASCII", "ignore")
