# -*- coding: utf-8 -*-

from emec import Institution

ies = Institution(2132)
ies.parse()

data_ies = ies.get_full_data()

ies.write_json('emec.json')

