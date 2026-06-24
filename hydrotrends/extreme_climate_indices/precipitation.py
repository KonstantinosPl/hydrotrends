import os

import pandas as pd

from hydrotrends.climatology.seasons import MONTHS
from hydrotrends.io.excel import save_monthly_excel, save_annual_excel

def precipitation_extreme_indices(input_file_path, output_dir):
    data = pd.read_csv(input_file_path)

    data["valid_time"] = pd.to_datetime(data["valid_time"])
    data["year"] = data["valid_time"].dt.year
    data["month"] = data["valid_time"].dt.month
    data["month_name"] = data["month"].map(MONTHS)

    data = data.sort_values(["name", "valid_time"]).reset_index(drop=True)

    data["wet_day"] = data["tp"] >= 1
    data["dry_day"] = data["tp"] < 1


    rx1day = (data
    .groupby(["name", "year", "month_name"])["tp"]
    .max()
    .reset_index(name="Rx1day")
    )

    data["Rx5day_window"] = (
        data
        .groupby("name")["tp"]
        .rolling(window=5, min_periods=5)
        .sum()
        .reset_index(level=0, drop=True)
    )
    rx5day = (
        data
        .groupby(["name", "year", "month_name"])["Rx5day_window"]
        .max()
        .reset_index(name="Rx5day")
    )

    sdii_monthly = (
        data[data["wet_day"]]
        .groupby(["name", "year", "month_name"])["tp"]
        .mean()
        .reset_index(name="SDII")
    )

    sdii_annual = (
        data[data["wet_day"]]
        .groupby(["name", "year"])["tp"]
        .mean()
        .reset_index(name="SDII")
    )
    
    r10mm = (data[data["tp"] >= 10]
         .groupby(["name", "year"])["tp"]
         .count()
         .reset_index(name="R10mm")
         )

    r20mm = (data[data["tp"] >= 20]
            .groupby(["name", "year"])["tp"]
            .count()
            .reset_index(name="R20mm")
            )
    
    def max_consecutive_spell(series):
        groups = (series != series.shift()).cumsum()
        
        return series.groupby(groups).sum().max()
    
    cdd = (data
       .groupby(["name", "year"])["dry_day"]
       .apply(max_consecutive_spell)
       .reset_index(name="CDD")
       )

    cwd = (
        data
        .groupby(["name", "year"])["wet_day"]
        .apply(max_consecutive_spell)
        .reset_index(name="CWD")
    )

    prcptot = (
        data[data["wet_day"]]
        .groupby(["name", "year"])["tp"]
        .sum()
        .reset_index(name="PRCPTOT")
    )

    save_monthly_excel(rx1day, "Rx1day", os.path.join(output_dir, "Rx1day.xlsx"))
    save_monthly_excel(rx5day, "Rx5day", os.path.join(output_dir, "Rx5day.xlsx"))
    save_monthly_excel(sdii_monthly, "SDII", os.path.join(output_dir, "SDII_monthly.xlsx"))

    save_annual_excel(sdii_annual, "SDII", os.path.join(output_dir, "SDII_annual.xlsx"))
    save_annual_excel(r10mm, "R10mm", os.path.join(output_dir, "R10mm.xlsx"))
    save_annual_excel(r20mm, "R20mm", os.path.join(output_dir, "R20mm.xlsx"))
    save_annual_excel(cdd, "CDD", os.path.join(output_dir, "CDD.xlsx"))
    save_annual_excel(cwd, "CWD", os.path.join(output_dir, "CWD.xlsx"))
    save_annual_excel(prcptot, "PRCPTOT", os.path.join(output_dir, "PRCPTOT.xlsx"))

    return