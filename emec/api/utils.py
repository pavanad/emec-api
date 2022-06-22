# -*- coding: utf-8 -*-

from unicodedata import normalize


def normalize_key(key: str) -> str:
    """Formata a chave para ser utilizada no json.

    Args:
        key (str): Campo coletado no scraping dos dados do MEC.

    Returns:
        str: Retorna a sttring formatada para ser utilizada no json.
    """
    aux = key.strip(" :").replace(" ", "_").lower()
    aux = aux.replace("_-_sigla", "")

    return normalize("NFKD", aux).encode("ASCII", "ignore")
