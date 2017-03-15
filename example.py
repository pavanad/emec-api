# -*- coding: utf-8 -*-

from emec import Institution

ies = Institution(2132)
ies.parse()

ies.write_json('emec.json')

