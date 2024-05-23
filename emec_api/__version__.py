# -*- coding: utf-8 -*-

__author__ = "Adilson Pavan"

VERSION = (0, 1, 8)


def get_version():
    version = f"{VERSION[0]}.{VERSION[1]}"
    if VERSION[2]:
        version = f"{version}.{VERSION[2]}"
    return version


__version__ = get_version()
