# -*- coding: utf-8 -*-

import time
from emec.api.client import Institution


start = time.time()
ies = Institution(22)
ies.parse()
elapsed = time.time() - start
print(f"Elapsed: {elapsed}")

# export to json
ies.to_json("emec.json")

# export to csv
ies.to_csv("emec.csv")
