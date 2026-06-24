import xarray as xr

def load_grib(input_file):
    data = xr.open_dataset(input_file, engine="cfgrib", decode_timedelta=True)
    var_name = list(data.data_vars)[0]
    return data, data[var_name]
