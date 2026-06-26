import os

from hydrotrends.io.load import _read_table

def rank_regions(values_path, trends_path, n, output_dir, ranking=None, sheet_nr=0):
    values_df = _read_table(values_path, sheet_nr)
    trends_df = _read_table(trends_path, sheet_nr)

    year_cols = [col for col in values_df.columns if str(col).isdigit()]

    summary_df = values_df[["name"]].copy()
    summary_df["mean_value"] = values_df[year_cols].mean(axis=1)
    summary_df["min_value"] = values_df[year_cols].min(axis=1)
    summary_df["max_value"] = values_df[year_cols].max(axis=1)
    summary_df["min_date"] = values_df[year_cols].idxmin(axis=1)
    summary_df["max_date"] = values_df[year_cols].idxmax(axis=1)

    merged = trends_df.merge(summary_df, on="name", how="inner")

    if ranking == "highest":
        ranked = merged.sort_values("slope", ascending=False)
    elif ranking == "lowest":
        ranked = merged.sort_values("slope", ascending=True)
    else:
        raise ValueError("ranking must be 'highest' or 'lowest'")
    
    ranked = ranked.head(n)
    ranked.reset_index(drop=True, inplace=True)
    ranked.insert(0, "rank", range(1, len(ranked) + 1))

    output_folder = os.path.join(output_dir, "summaries")
    os.makedirs(output_folder, exist_ok=True)

    ranked.to_csv(os.path.join(output_folder, f"rank_regions_{ranking}.csv"), index=False)
    return ranked