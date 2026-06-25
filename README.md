#HydroTrends

HydroTrends is an open-source Python package for hydroclimatic trend analysis of gridded climate datasets. It provides tools for polygon-based spatial aggregation, temporal aggregation, climate extreme indices, and non-parametric trend analysis using the Mann–Kendall test.

The package is designed for reproducible hydroclimatic analyses at different spatial scales, such as river basins, water districts, catchments, or any user-defined polygon layer.


##Example 

```python
from hydrotrends import run_trend_workflow

variable_paths = [
    precipitation_monthly_path,
    temperature_monthly_path,
]
shapefiles = {
    "water_districts": water_districts_path,
    "basins": basins_path
}
unit_conversion = {
    "t2m": kelvin_to_celsius
}

run_trend_workflow(
    variable_paths=variable_paths,
    shapefiles=shapefiles,
    output_dir="outputs",
    modes=("monthly", "seasonal", "annual"),
    time_dim="valid_time",
    unit_conversions=unit_conversion
)
```
