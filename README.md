HydroTrends

HydroTrends is an open-source Python package for hydroclimatic trend analysis of gridded climate datasets. It provides tools for polygon-based spatial aggregation, temporal aggregation, climate extreme indices, and non-parametric trend analysis using the Mann–Kendall test.

The package is designed for reproducible hydroclimatic analyses at different spatial scales, such as river basins, water districts, catchments, or any user-defined polygon layer.


```python
from hydrotrends import run_trend_workflow

variable_paths = [
    precipitation_monthly_path,
    temperature_monthly_path,
]

run_trend_workflow(
    variable_paths=variable_paths,
    shapefiles=shapefiles,
    output_dir="outputs",
)
```
