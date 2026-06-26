from pathlib import Path

import geopandas as gpd
import xagg as xa
import xarray as xr

import pandas as pd 

from hydrotrends.calendar.constants import MONTHS, MONTHS_ORDER, SEASONS, SEASONS_ORDER
from hydrotrends.aggregation.polygon_aggregation import apply_weightmap
from hydrotrends.io.excel import save_grouped_excel
from hydrotrends.io.load import _load_dataset

def _infer_time_step(df, time_dim):
    time_values = pd.to_datetime(df[time_dim]).sort_values()
    return time_values.diff().dropna().median()

def aggregate_daily(input_folder_path, shapefile_path, output_dir, time_dim=None, unit_conversions=None):
    input_folder_path = Path(input_folder_path)
    output_dir = Path(output_dir)

    files = sorted(input_folder_path.glob("*.nc"))
    if not files:
        raise FileNotFoundError(f"No .nc files found in input folder: {input_folder_path}")

    shapefile = gpd.read_file(shapefile_path)

    results = []
    
    ds_first = xr.open_dataset(files[0], engine="netcdf4")
    var_name = list(ds_first.data_vars)[0]

    data_first = ds_first[var_name]
    _, weightmap = apply_weightmap(data_first, shapefile)

    data_first.close()

    for file in files:
        with xr.open_dataset(file, engine="netcdf4") as ds:
            data = ds[var_name]
            poly_data = xa.aggregate(data, weightmap).to_dataframe().reset_index()
        
        time_step = _infer_time_step(poly_data, time_dim)

        if var_name == "t2m":
            if time_step >= pd.Timedelta(days=1):
                raise ValueError(
                    "Input temperature data are daily. To compute temperature extreme indices, sub-daily data are required."
                                 )
             
            daily = (
                poly_data
                .groupby("name")
                .resample("1D", on=time_dim)[var_name]
                .agg(
                    t2m_mean="mean",
                    t2m_max="max",
                    t2m_min="min"
                )
                .reset_index()
            )

            if unit_conversions is not None and var_name in unit_conversions:
                for col in ["t2m_mean", "t2m_max", "t2m_min"]:
                    daily[col] = unit_conversions[var_name](daily[col])

        elif var_name == "tp":
            if time_step < pd.Timedelta(days=1):
                daily = (
                    poly_data
                    .groupby("name")
                    .resample("1D", on=time_dim)[var_name]
                    .sum()
                    .reset_index()
                )
                        
            else:
                daily = poly_data.copy()
            
            if unit_conversions is not None and var_name in unit_conversions:
                daily[var_name] = unit_conversions[var_name](daily[var_name])

        else:
            raise ValueError(
                f"Unsupported variable '{var_name}'. " "aggregate_daily currently supports only 't2m' and 'tp'.")

        results.append(daily)
        
    daily_polygon_df = pd.concat(results, ignore_index=True)
    
    output_folder = output_dir / f"{var_name}" / "daily"
    output_folder.mkdir(parents=True, exist_ok=True)

    output_path = output_folder / "daily_values.csv"
    daily_polygon_df.to_csv(output_path, index=False)

    return daily_polygon_df


def aggregate_monthly(input_file, shapefile_path, output_folder, time_dim=None, unit_conversions=None):
    xa.set_options(silent=True)

    output_folder = Path(output_folder)

    shapefile = gpd.read_file(shapefile_path)

    data, data_array = _load_dataset(input_file)

    var_name = data_array.name  # Retrieve the variable name of the grib e.g. tp, t2m

    overlay, _ = apply_weightmap(data_array, shapefile)
   
    mean_per_polygon_df = overlay.to_dataframe()
    
    if unit_conversions is not None and var_name in unit_conversions:
        mean_per_polygon_df[var_name] = unit_conversions[var_name](
            mean_per_polygon_df[var_name]
        )
    
    monthly= mean_per_polygon_df.reset_index().drop("poly_idx", axis=1)
    
    monthly = monthly.assign(
                year=monthly[time_dim].dt.year,
                month=monthly[time_dim].dt.month)
    
    if var_name == "tp":
        agg_function = "sum"
    else:
        agg_function = "mean"

    # Mean or Total monthly
    monthly_grouped = ((monthly.groupby(["name", "month", "year"], as_index=False).agg(monthly=(var_name, agg_function))).round(2))
    monthly_grouped["month_name"] = monthly_grouped["month"].map(MONTHS)  
    monthly_grouped = monthly_grouped.sort_values(["name", "month"])
    monthly_grouped["month_name"] = pd.Categorical(
        monthly_grouped["month_name"],
        categories=MONTHS_ORDER,
        ordered=True
    )

    # Mean or Total annual
    annual = (
        monthly
        .groupby(["name", "year"], as_index=False)
        .agg(annual=(var_name, agg_function))
        .round(2)
    )
    annual_wide = annual.pivot(index="name", columns="year", values="annual")
    annual_wide["mean"] = annual_wide.mean(axis=1)
    annual_wide = annual_wide.reset_index()

    monthly["season"] = monthly["month"].map(SEASONS)
    monthly["season_year"] = monthly["year"]
    monthly.loc[monthly["month"] == 12, "season_year"] += 1

    # Mean or Total seasonal
    seasonal_grouped = (monthly.groupby(["name", "season_year", "season"], as_index=False)
                                 .agg(seasonal=(var_name, agg_function))
                                 .round(2))
    seasonal_grouped["season"] = pd.Categorical(
            seasonal_grouped["season"],
            categories=SEASONS_ORDER,
            ordered=True
    )
    seasonal_grouped = seasonal_grouped.sort_values(["name", "season_year", "season"])    

    output_folder_monthly = output_folder / var_name / "monthly"
    output_folder_annual = output_folder / var_name / "annual"
    output_folder_seasonal = output_folder / var_name / "seasonal"

    output_folder_monthly.mkdir(parents=True, exist_ok=True)
    output_folder_annual.mkdir(parents=True, exist_ok=True)
    output_folder_seasonal.mkdir(parents=True, exist_ok=True)


    save_grouped_excel(
        df=monthly_grouped,
        group_col="name",
        index_col="year",
        columns_col="month_name",
        values_col="monthly",
        output_path=output_folder_monthly / f"monthly_{var_name}.xlsx",
        column_order=MONTHS_ORDER,
    )

    save_grouped_excel(
        df=seasonal_grouped,
        group_col="name",
        index_col="season_year",
        columns_col="season",
        values_col="seasonal",
        output_path=output_folder_seasonal / f"seasonal_{var_name}.xlsx",
        column_order=SEASONS_ORDER,
    )
            
    annual_wide.to_excel(output_folder_annual /f"annual_{var_name}.xlsx") 

    seasonal_dict = {
        name: group.pivot(
            index="season_year",
            columns="season",
            values="seasonal"
        ).reset_index()
        for name, group in seasonal_grouped.groupby("name")
    }  
    return var_name, annual_wide, seasonal_dict