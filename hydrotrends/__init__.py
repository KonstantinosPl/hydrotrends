"""
HydroTrends: hydroclimatic trend analysis tools.
"""

__version__ = "0.1.0"

from hydrotrends.analysis import (
    estimate_mean_per_polygon_from_monthly_file,
    mann_kendall_test,
    compute_daily_stats_by_polygon,
)

from hydrotrends.extreme_climate_indices.temperature import (
    temperature_extreme_indices,
)

from hydrotrends.extreme_climate_indices.precipitation import (
    precipitation_extreme_indices,
)

from hydrotrends.workflow import (
    run_trend_workflow
)