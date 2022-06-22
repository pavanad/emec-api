# -*- coding: utf-8 -*-

import time
from emec.api.client import Institution


start = time.time()
ies = Institution(22)
ies.parse()
elapsed = time.time() - start
print(f"Elapsed: {elapsed}")

ies.write_json("emec.json")
