import pandas as pd

from hydrotrends.calendar.constants import MONTHS_ORDER

def save_annual_excel(df, value_col, output_path):
    annual_wide = df.pivot(
        index="name",
        columns="year",
        values=value_col
    ).reset_index()

    annual_wide.to_excel(output_path, index=False)

def save_monthly_excel(df, value_col, output_path):
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for district, district_df in df.groupby("name"):

            monthly_wide = district_df.pivot(
                index="year",
                columns="month_name",
                values=value_col
            )

            monthly_wide = monthly_wide.reindex(columns=MONTHS_ORDER)
            monthly_wide.to_excel(
                writer,
                sheet_name=str(district)[:31]
            )

def save_grouped_excel(
    df,
    group_col,
    index_col,
    columns_col,
    values_col,
    output_path,
    column_order=None,
):
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for group_name, group_df in df.groupby(group_col):
            wide = group_df.pivot(
                index=index_col,
                columns=columns_col,
                values=values_col
            )
            if column_order is not None:
                wide = wide.reindex(columns=column_order)
            wide.to_excel(writer, sheet_name=str(group_name)[:31])
    
