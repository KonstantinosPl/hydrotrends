import os

import matplotlib.pyplot as plt

import xagg as xa
import geopandas as gpd

from hydrotrends.io.load import load_dataset

def apply_weightmap(data_array, shapefile):
    xa.set_options(silent=True)

    weightmap = xa.pixel_overlaps(data_array, shapefile)
    overlay = xa.aggregate(data_array, weightmap)
    return overlay, weightmap

def save_weightmap_plots(weightmap, data_array, shapefile, output_folder):
    output_folder_xagg = os.path.join(output_folder, "xagg_plots")
    os.makedirs(output_folder_xagg, exist_ok=True)
    print("Saving plots to:", output_folder_xagg)

    for i, name in enumerate(shapefile["name"]):
        fig, _ = weightmap.diag_fig(i, data_array)
        fig.set_size_inches(15, 8)
        
        # remove any existing figure-level text
        for txt in list(fig.texts):
            txt.remove()
        # remove axes titles/text that diag_fig may have added
        for a in fig.axes:
            a.set_title("")
            for txt in list(a.texts):
                txt.remove()

        fig.suptitle(f"Polygon: {name}", fontsize=12)
        fig.savefig(os.path.join(output_folder_xagg, f"{name}_overlay.svg"), bbox_inches="tight")

        plt.close(fig)
    return

def create_weightmap_plots(filepath, shapefile_path, save_plots=False, plot_output_dir=None):

    polygons = gpd.read_file(shapefile_path)
    _, data_array = load_dataset(filepath)
    overlay, weightmap = apply_weightmap(data_array, polygons)
    
    if save_plots:
        save_weightmap_plots(
            weightmap,
            data_array,
            polygons,
            plot_output_dir,
        )

    return overlay, weightmap

