# HydroTrends

HydroTrends is an open-source Python package for hydroclimatic trend analysis of gridded climate datasets. It provides tools for polygon-based spatial aggregation, temporal aggregation, climate extreme indices, and non-parametric trend analysis using the Mann–Kendall test.

The package is designed for reproducible hydroclimatic analyses at different spatial scales, such as river basins, water districts, catchments, or any user-defined polygon layer.


## Features

### Spatial Analysis
- Polygon-based and pixel-weighted aggregation using xagg tool
- Area-weighted statistics
- Any polygon layer 

### Temporal Aggregation
- Daily
- Monthly
- Seasonal
- Annual

### Climate Indices
ETCCDI-based Climate Extreme Indices:

    **Temperature** 
        - SU
        - TXx
        - TNx
        - DTR
    
    **Precipitation**
        - Rx1Day
        - Rx5Day
        - SDII
        - R10mm
        - R20mm
        - CDD
        - CWD
        - PRCPTOT

### Trend analysis
- Mann Kendall Test
- Sen's Slope
- Spatial outputs (GeoPackage)


## Installation
Clone the repository:

```bash
git clone https://github.com/yourusername/hydrotrends.git
cd hydrotrends
```

Install the package:

```bash
pip install -e .
```



## Example 

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
