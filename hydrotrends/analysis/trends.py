
import geopandas as gpd
import os

import pandas as pd 

import pymannkendall as mk

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