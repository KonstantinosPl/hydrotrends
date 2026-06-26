import os
from pathlib import Path

import xarray as xr
import pandas as pd

def _load_dataset(input_file):
    ext = os.path.splitext(input_file)[1].lower()

    if ext == ".grib":
        data = xr.open_dataset(input_file, engine="cfgrib", decode_timedelta=True)
    elif ext ==".nc":
        data = xr.open_dataset(input_file, engine="h5netcdf", decode_timedelta=True)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Expected .grib or .nc.")
    
    var_name = list(data.data_vars)[0]
    return data, data[var_name]

def _read_table(path, sheet_nr=0):
    path = Path(path)

    suffix = path.suffix.lower()

    if suffix == ".csv":
        return pd.read_csv(path)
    elif suffix in [".xlsx", ".xls"]:
        return pd.read_excel(path, sheet_nr)
    else:
        raise ValueError("Input must be .csv, .xlsx, .xls")

