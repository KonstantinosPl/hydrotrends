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
git clone https://github.com/KonstantinosPl/hydrotrends.git
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


## Workflows

### `run_trend_workflow()`

Performs spatial aggregation, temporal aggregation, and non-parametric trend analysis for gridded climate datasets.

**Outputs**

- Monthly aggregated time series (`.xlsx`)
- Seasonal aggregated time series (`.xlsx`)
- Annual aggregated time series (`.xlsx`)
- Monthly Mann–Kendall trend statistics (`.csv`, `.gpkg`)
- Seasonal Mann–Kendall trend statistics (`.csv`, `.gpkg`)
- Annual Mann–Kendall trend statistics (`.csv`, `.gpkg`)

---
### `run_temperature_indices_workflow()`

Computes ETCCDI temperature extreme indices from sub-daily temperature data.

**Outputs**

- Daily aggregated temperature (`.csv`)
- SU (`.xlsx`)
- TXx (`.xlsx`)
- TNx (`.xlsx`)
- DTR (`.xlsx`)
- Mann–Kendall trend statistics for all indices (`.csv`, `.gpkg`) *(optional)*

---

### `run_precipitation_indices_workflow()`

Computes ETCCDI precipitation extreme indices from daily or sub-daily precipitation data.

**Outputs**

- Daily aggregated precipitation (`.csv`)
- Rx1day (`.xlsx`)
- Rx5day (`.xlsx`)
- SDII (`.xlsx`)
- R10mm (`.xlsx`)
- R20mm (`.xlsx`)
- CDD (`.xlsx`)
- CWD (`.xlsx`)
- PRCPTOT (`.xlsx`)
- Mann–Kendall trend statistics for all indices (`.csv`, `.gpkg`) *(optional)*


Depending on the selected workflow, HydroTrends generates:

- CSV files
- Excel workbooks
- GeoPackage layers
- Trend statistics
- Climate extreme indices


