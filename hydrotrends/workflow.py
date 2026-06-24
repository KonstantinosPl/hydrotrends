from pathlib import Path

from hydrotrends.analysis import (estimate_mean_per_polygon_from_monthly_file, mann_kendall_test)

def run_trend_workflow(
    variable_paths,
    shapefiles,
    output_dir,
    modes=("monthly", "seasonal", "annual"),
):
    output_dir = Path(output_dir)

    for input_file in variable_paths:

        for region_name, shapefile_path  in shapefiles.items():
            
            region_output_dir = output_dir / region_name

            var_name = estimate_mean_per_polygon_from_monthly_file(
                input_file=input_file,
                shapefile_path=shapefile_path,
                output_folder=region_output_dir,
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