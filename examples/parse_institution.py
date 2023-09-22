# -*- coding: utf-8 -*-

import time
from emec.api.client import Institution


start = time.time()
ies = Institution(22)
ies.parse()
elapsed = time.time() - start
print(f"Elapsed: {elapsed}")

df_inst = ies.get_institution_dataframe()
print(df_inst.head())

df_campus = ies.get_campus_dataframe()
print(df_campus.head())

df_courses = ies.get_courses_dataframe()
print(df_courses.head())

# export to json
ies.to_json("emec.json")

# export to csv
ies.to_csv("emec.csv")
