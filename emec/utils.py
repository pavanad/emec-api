# -*- coding: utf-8 -*-

from unicodedata import normalize

def normalize_key(key):
    """
    Formata a chave para ser utilizada no json.
    
    Args:
        key (string):    Campo coletado no scraping dos dados do MEC.
        
    Returns:
        Retorna a sttring formatada para ser utilizada no json.
    """
    
    aux = key.strip(' :').replace(' ', '_').lower()
    aux = aux.replace('_-_sigla', '')
    
    return normalize('NFKD', aux).encode('ASCII','ignore')


    