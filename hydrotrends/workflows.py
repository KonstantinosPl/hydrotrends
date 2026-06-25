from pathlib import Path

from hydrotrends.analysis import aggregate_daily, aggregate_monthly, mann_kendall_test
from hydrotrends.extreme_climate_indices.temperature import temperature_extreme_indices
from hydrotrends.extreme_climate_indices.precipitation import precipitation_extreme_indices

def run_trend_workflow(
    variable_paths,
    shapefiles,
    output_dir,
    modes=("monthly", "seasonal", "annual"),
    time_dim=None,
    unit_conversions=None
):
    output_dir = Path(output_dir)

    for input_file in variable_paths:

        for region_name, shapefile_path  in shapefiles.items():
            
            region_output_dir = output_dir / region_name

            var_name = aggregate_monthly(
                input_file=input_file,
                shapefile_path=shapefile_path,
                output_folder=region_output_dir,
                time_dim=time_dim,
                unit_conversions=unit_conversions
            )

            for mode in modes:

                 for mode in modes:
                    mk_input_file = (
                        region_output_dir
                        / var_name
                        / mode
                        / f"{mode}_{var_name}.xlsx"
                    )

                    mann_kendall_test(
                        input_file=mk_input_file,
                        shapefile_path=shapefile_path,
                        output_folder=region_output_dir,
                        var_name=var_name,
                        mode=mode,
                    )
    return

TEMPERATURE_INDICES = [
    ("SU", "SU.xlsx", "annual"),
    ("TXx", "TXx.xlsx", "monthly"),
    ("TNx", "TNx.xlsx", "monthly"),
    ("DTR", "DTR.xlsx", "monthly"),
]

PRECIPITATION_INDICES = [
    ("Rx1day", "Rx1day.xlsx", "monthly"),
    ("Rx5day", "Rx5day.xlsx", "monthly"),
    ("SDII_monthly", "SDII_monthly.xlsx", "monthly"),
    ("SDII_annual", "SDII_annual.xlsx", "annual"),
    ("R10mm", "R10mm.xlsx", "annual"),
    ("R20mm", "R20mm.xlsx", "annual"),
    ("CDD", "CDD.xlsx", "annual"),
    ("CWD", "CWD.xlsx", "annual"),
    ("PRCPTOT", "PRCPTOT.xlsx", "annual"),
]


def run_temperature_indices_workflow(
    input_folder,
    shapefiles,
    output_dir,
    calculate_trends=True,
    time_dim=None,
    unit_conversions=None

):
    output_dir = Path(output_dir)

    for region_name, shapefile_path in shapefiles.items():
        region_output_dir = output_dir / region_name
        indices_dir = region_output_dir / "t2m" / "daily"

        aggregate_daily(
            input_folder_path=input_folder,
            shapefile_path=shapefile_path,
            output_dir=region_output_dir,
            time_dim=time_dim,
            unit_conversions=unit_conversions
        )

        temperature_extreme_indices(
            input_file_path=indices_dir / "daily_values.csv",
            output_dir=indices_dir,
        )

        if calculate_trends:
            for var_name, filename, mode in TEMPERATURE_INDICES:
                mann_kendall_test(
                    input_file=indices_dir / filename,
                    shapefile_path=shapefile_path,
                    output_folder=indices_dir,
                    var_name=var_name,
                    mode=mode,
                )

    return


def run_precipitation_indices_workflow(
    input_folder,
    shapefiles,
    output_dir,
    calculate_trends=True,
    time_dim=None,
    unit_conversions=None
):
    output_dir = Path(output_dir)

    for region_name, shapefile_path in shapefiles.items():
        region_output_dir = output_dir / region_name
        indices_dir = region_output_dir / "tp" / "daily"

        aggregate_daily(
            input_folder_path=input_folder,
            shapefile_path=shapefile_path,
            output_dir=region_output_dir,
            time_dim=time_dim,
            unit_conversions=unit_conversions
        )

        precipitation_extreme_indices(
            input_file_path=indices_dir / "daily_values.csv",
            output_dir=indices_dir,
        )

        if calculate_trends:
            for var_name, filename, mode in PRECIPITATION_INDICES:
                mann_kendall_test(
                    input_file=indices_dir / filename,
                    shapefile_path=shapefile_path,
                    output_folder=indices_dir,
                    var_name=var_name,
                    mode=mode,
                )

    return