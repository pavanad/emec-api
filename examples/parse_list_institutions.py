import time

import pandas as pd

from emec_api.api.client import Institution

MAX_RETRIES = 10


def main():
    df = pd.read_csv("examples/data/list_institutions.csv")
    df.drop_duplicates(subset=["Código da IES"], inplace=True)

    df_consolidate = pd.DataFrame()
    code_ies = df["Código da IES"].tolist()

    for code in code_ies:
        retries = 0
        success = False
        print(f"\nParsing {code}...")

        while retries < MAX_RETRIES and not success:
            try:
                ies = Institution(code)
                ies.parse()
                df_courses = ies.get_courses_dataframe()
                df_consolidate = pd.concat(
                    [df_consolidate, df_courses], ignore_index=True
                )
                success = True
            except Exception as error:
                print(error)
                print(f"Retrying parsing {code}...")

                retries += 1
                time.sleep(2)

    df_consolidate.to_csv("examples/data/parsed_institutions.csv", index=False)


if __name__ == "__main__":
    main()
