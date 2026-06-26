from pathlib import Path
import os

import numpy as np
import matplotlib.pyplot as plt

from hydrotrends.calendar.constants import SEASONS_ORDER

VARIABLE_LABELS = {
    "tp": "Precipitation (mm)",
    "t2m": "Air temperature (°C)",
    "pev": "Potential evapotranspiration (mm)",
    "sro": "Surface runoff (mm)",
    "swvl_total": "Soil moisture (m³ m⁻³)"
}

def plot_annual_means(data, var_name, output_dir):
    output_dir = Path(output_dir)
    output_folder = output_dir / var_name / "annual"
    
    colors = plt.cm.tab20(np.linspace(0, 1, len(data)))

    year_cols = [col for col in data.columns if str(col).isdigit()]
    plt.figure(figsize=(16, 8))
    
    ylabel = VARIABLE_LABELS.get(var_name, var_name)
    for (_, row), color in zip(data.iterrows(), colors):
        plt.plot(
                year_cols,
                row[year_cols], 
                color=color,
                label=row["name"]
            ) 

    plt.xticks(year_cols[::5], fontsize=10)
    plt.xlabel("Year", fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.title(f"Annual {ylabel}", fontsize=14)
    plt.grid(alpha=0.3)

    if len(data) <= 20:
        plt.legend(
            bbox_to_anchor=(1.02, 1),
            loc="upper left",
            fontsize=10
        )

    plt.tight_layout()
    plt.savefig(output_folder / f"annual_{var_name}.svg", format="svg")
    plt.close()
    return

def plot_seasonal_means(data, var_name, output_dir):
    output_dir = Path(output_dir)
    output_folder = output_dir / var_name / "seasonal"

    colors = plt.cm.tab20(np.linspace(0, 1, len(data)))
    ylabel = VARIABLE_LABELS.get(var_name, var_name)

    for season in SEASONS_ORDER:
        plt.figure(figsize=(16, 8))

        for (region, df), color in zip(data.items(), colors):
            plt.plot(
                df["season_year"],
                df[season],
                color=color,
                label=region
            )

        plt.xticks(df["season_year"][::5], fontsize=10)
        plt.xlabel("Year", fontsize=12)
        plt.ylabel(ylabel, fontsize=12)
        plt.title(f"{season} {ylabel}", fontsize=14)
        plt.grid(alpha=0.3)

        if len(data) <= 20:
            plt.legend(
                bbox_to_anchor=(1.02, 1),
                loc="upper left",
                fontsize=10
            )
        plt.tight_layout()
        plt.savefig(output_folder / f"{season}_{var_name}.svg", format="svg")
        plt.close()    
    return
