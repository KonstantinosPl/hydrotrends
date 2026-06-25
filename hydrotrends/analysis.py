from pathlib import Path

import geopandas as gpd
import xagg as xa
import xarray as xr

import os

import pandas as pd 

import pymannkendall as mk

from hydrotrends.climatology.seasons import MONTHS, SEASONS, SEASONS_ORDER
from hydrotrends.aggregation.polygon_aggregation import apply_weightmap
from hydrotrends.transforms.units import kelvin_to_celsius, m_to_mm
from hydrotrends.io.excel import save_grouped_excel
from hydrotrends.io.load import load_dataset

def aggregate_daily(input_folder_path, shapefile_path, output_dir):
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
        
        if var_name == "t2m":
            daily = (
                poly_data
                .groupby("name")
                .resample("1D", on="valid_time")[var_name]
                .agg(
                    t2m_mean="mean",
                    t2m_max="max",
                    t2m_min="min"
                )
                .reset_index()
            )

            daily[["t2m_mean", "t2m_max", "t2m_min"]] = kelvin_to_celsius(daily[["t2m_mean", "t2m_max", "t2m_min"]])
            results.append(daily)

        elif var_name == "tp":
            daily = poly_data.copy()
            daily["tp"] = m_to_mm(daily["tp"])

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


def aggregate_monthly(input_file, shapefile_path, output_folder):
    xa.set_options(silent=True)

    output_folder = Path(output_folder)

    shapefile = gpd.read_file(shapefile_path)

    data, data_array = load_dataset(input_file)

    var_name = data_array.name  # Retrieve the variable name of the grib e.g. tp, t2m

    overlay, _ = apply_weightmap(data_array, shapefile)
   
    mean_per_polygon_df = overlay.to_dataframe()
    
    if var_name == "t2m":
        mean_per_polygon_df[var_name] = kelvin_to_celsius(mean_per_polygon_df[var_name])
    elif var_name in ["tp"]: 
        mean_per_polygon_df[var_name] = m_to_mm(mean_per_polygon_df[var_name])
    

    monthly= mean_per_polygon_df.reset_index().drop("poly_idx", axis=1)
    
    monthly = monthly.assign(
                year=monthly["time"].dt.year,
                month=monthly["time"].dt.month)
    
    if var_name == "tp":
        agg_function = "sum"
    else:
        agg_function = "mean"

    # Mean or Total monthly
    monthly_grouped = ((monthly.groupby(["name", "month", "year"], as_index=False).agg(monthly=(var_name, agg_function))).round(2))
    monthly_grouped["month_name"] = monthly_grouped["month"].map(MONTHS)  
    monthly_grouped = monthly_grouped.sort_values(["name", "month"])
    month_order = list(MONTHS.values())
    monthly_grouped["month_name"] = pd.Categorical(
        monthly_grouped["month_name"],
        categories=month_order,
        ordered=True
    )

    # Mean or Total annual
    annual = (
        monthly
        .groupby(["name", "year"], as_index=False)
        .agg(annual=(var_name, agg_function))
        .round(2)
    )
    annual_wide = (annual.pivot(index="name", columns="year", values="annual"))
    annual_wide["mean"] = annual_wide.mean(axis=1)

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
        column_order=month_order,
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
    return var_name



def mann_kendall_test(input_file, shapefile_path, output_folder, var_name, mode="monthly"):
    results = []
    shapefile = gpd.read_file(shapefile_path)
    
    if mode in ["monthly", "seasonal"]:
        data = pd.read_excel(input_file, sheet_name=None)
        
        if mode == "monthly":
            index_col = "year"
            period_label = "month"
            output_name = "monthly_trend_per_month"
        else:
            index_col = "season_year"
            period_label = "season"
            output_name = "seasonal_trend"    

        for district_name, df in data.items():
            period_cols = [col for col in df.columns if col != index_col]
        
            for period in period_cols:
                series = pd.to_numeric(df[period], errors="coerce")
                mk_result = mk.original_test(series)
            
                results.append({
                        "name": district_name,
                        period_label: period,
                        "trend": mk_result.trend,
                        "h": mk_result.h,
                        "p_value": mk_result.p,
                        "s": mk_result.s,
                        "slope": mk_result.slope,
                        "tau": mk_result.Tau,
                        "z": mk_result.z
                    })
                
    elif mode=="annual":
        data = pd.read_excel(input_file)

        year_cols = [col for col in data.columns if col != "name"]
        output_name = "annual_trend"

        for _, row in data.iterrows():
            series = pd.to_numeric(row[year_cols], errors="coerce")
            mk_result = mk.original_test(series)

            results.append({
                "name": row["name"],
                "period": "annual",
                "trend": mk_result.trend,
                "h": mk_result.h,
                "p_value": mk_result.p,
                "s": mk_result.s,
                "slope": mk_result.slope,
                "tau": mk_result.Tau,
                "z": mk_result.z
            })
    else:
        raise ValueError("mode must be 'monthly', 'seasonal', or 'annual'")

    results_df = pd.DataFrame(results)
    
    mode_folder = os.path.join(output_folder, f"{var_name}", f"{mode}")
    os.makedirs(mode_folder, exist_ok=True)
    trend_folder = os.path.join(mode_folder, "trends")
    os.makedirs(trend_folder, exist_ok=True)
    
    results_df.to_csv(os.path.join(trend_folder, f"{output_name}.csv"), index=False)

    mk_gdf = gpd.GeoDataFrame(
        results_df.merge(
            shapefile[["name", "geometry"]].drop_duplicates("name"),
            on="name",
            how="left"
        ),
        geometry="geometry",
        crs=shapefile.crs
    )

    mk_gdf.to_file(os.path.join(trend_folder, f"{output_name}.gpkg"), layer=f"{var_name}_trend", driver="GPKG")

    return  