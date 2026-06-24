import os 

import pandas as pd

from hydrotrends.io.excel import save_monthly_excel
from hydrotrends.climatology.seasons import MONTHS

def temperature_extreme_indices(input_file_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    data = pd.read_csv(input_file_path)
    
    data["valid_time"] = pd.to_datetime(data["valid_time"])
    data["year"] = data["valid_time"].dt.year
    data["month"] = data["valid_time"].dt.month
    data["month_name"] = data["month"].map(MONTHS)
    
    data["SU_day"] = data["t2m_max"] > 25

    su = (data
      .groupby(["name", "year"])["SU_day"]
      .sum()
      .reset_index(name="SU")
      )
    su = su.pivot(
        index="name",
        columns="year",
        values="SU"
    ).reset_index()

    txx = (data
        .groupby(["name", "year", "month_name"])["t2m_max"]
        .max()
        .reset_index(name="TXx")
        )

    tnx = (data
        .groupby(["name", "year", "month_name"])["t2m_min"]
        .max()
        .reset_index(name="TNx")
        )

    data["dtr"] = data["t2m_max"] - data["t2m_min"]

    dtr = (data
        .groupby(["name", "year", "month_name"])["dtr"]
        .mean()
        .reset_index(name="DTR")
        )

    su.to_excel(os.path.join(output_dir, "SU.xlsx"), index=False)

    save_monthly_excel(txx, value_col="TXx", output_path=os.path.join(output_dir, "TXx.xlsx"))
    save_monthly_excel(tnx, value_col="TNx", output_path=os.path.join(output_dir, "TNx.xlsx"))
    save_monthly_excel(dtr, value_col="DTR", output_path=os.path.join(output_dir, "DTR.xlsx"))

    return