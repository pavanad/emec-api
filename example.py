# -*- coding: utf-8 -*-

from emec.api.client import Institution

ies = Institution(22)
ies.parse()

ies.write_json("emec.json")
