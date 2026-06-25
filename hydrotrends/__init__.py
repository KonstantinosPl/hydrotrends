"""
HydroTrends: hydroclimatic trend analysis tools.
"""

__version__ = "0.1.0"

from hydrotrends.analysis import (
    aggregate_monthly,
    mann_kendall_test,
    aggregate_daily,
)

from hydrotrends.extreme_climate_indices.temperature import (
    temperature_extreme_indices,
)

from hydrotrends.extreme_climate_indices.precipitation import (
    precipitation_extreme_indices,
)

from hydrotrends.workflows import (
    run_trend_workflow,
    run_temperature_indices_workflow, 
    run_precipitation_indices_workflow
)

from hydrotrends.aggregation.polygon_aggregation import (
    create_weightmap_plots
)