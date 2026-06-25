import os

import xarray as xr

def load_dataset(input_file):
    ext = os.path.splitext(input_file)[1].lower()

    if ext == ".grib":
        data = xr.open_dataset(input_file, engine="cfgrib", decode_timedelta=True)
    elif ext ==".nc":
        data = xr.open_dataset(input_file, engine="h5netcdf", decode_timedelta=True)
    else:
        raise ValueError(f"Unsupported file type: {ext}. Expected .grib or .nc.")
    
    var_name = list(data.data_vars)[0]
    return data, data[var_name]
