# -*- coding: utf-8 -*-

from unicodedata import normalize

def normalize_key(key):
    aux = key.strip(' :').replace(' ', '_').lower()
    aux = aux.replace('_-_sigla', '')
    return normalize('NFKD', aux).encode('ASCII','ignore')


    