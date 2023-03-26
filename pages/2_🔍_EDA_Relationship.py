# Script for second page of Streamlit on EDA
import pandas as pd
import numpy as np
import yaml
import streamlit as st
from src.utility import slice_features, slice_year_range, agg_date, plotly_violin, plotly_bar, plotly_line


with open("config.yml", encoding="utf-8", mode='r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.Loader)
    artifacts_path = cfg['eda']['artifacts_path']

# cache data to avoid reloading data
@st.cache_data(ttl=300)
def load_parquet(path_filename):
    """
    Loads a Parquet file located at the given path and filename into a pandas DataFrame.

    Args:
    - path_filename: string containing the path and filename of the Parquet file to be loaded

    Returns:
    - pandas DataFrame containing the contents of the Parquet file
    """
    
    # Use pandas' read_parquet() function to load the Parquet file into a DataFrame
    
    return pd.read_parquet(path_filename)


def main():
    """
    First page of Streamlit app to render EDA visualisations
    """

    st.set_page_config(
        page_title="Second page of streamlit app",
        page_icon='🏠',
        layout="wide",
    )

    st.title("Understanding the Relationships between Resale Price and other Features")

    # load data artifact
    df_load = load_parquet(f'{artifacts_path}/hdb_resale.parquet')

    # SIDEBAR
    with st.sidebar:

        # SELECT_SLIDER - YEAR RANGE
        date_range_lst = df_load.year.unique()
        date_range_lst.sort()

        start_year, end_year = st.select_slider(
            "Select range of years",
            options=date_range_lst,
            value=(date_range_lst[-11],date_range_lst.max())
        )
        st.write('You selected year range between', start_year, 'and', end_year)


        # MULTISELECT - FLAT TYPE
        flat_type_fields = df_load['flat_type'].unique()
        sel_flat_type = st.multiselect(
            "Select flat types",
            options=flat_type_fields
                )

        # MULTISELECT - TOWN
        town_fields = df_load['town'].unique()
        sel_town = st.multiselect(
                    "Select town",
                    options=town_fields
                )
        
        # MULTISELECT - FLAT MODEL
        flat_model_fields = df_load['flat_model'].unique()
        sel_flat_model = st.multiselect(
                    "Select flat model",
                    options=flat_model_fields
                )
        
        st.write("This dashboard is created by [Leon Sun](https://github.com/leonswl). The source code for this project is published in this [GitHub Repository](https://github.com/leonswl/hdb-resale).")

    # slice year range based on user's selected range
    df_resale = slice_year_range(df_load, start_year=start_year, end_year=end_year)
    df_resale = df_resale.copy().drop(['full_address','search_address','lease_commence_date'],axis=1)

    # If the selected flat type list is empty, set it to the default list of flat type fields.
    if len(sel_flat_type) == 0:
        sel_flat_type = flat_type_fields

    # If the selected town list is empty, set it to the default list of town fields.
    if len(sel_town) == 0:
        sel_town = town_fields

    # If the selected flat model list is empty, set it to the default list of flat model fields.
    if len(sel_flat_model) == 0:
        sel_flat_model = flat_model_fields

    # If all three filter lists are empty, create a copy of the input DataFrame.
    if (len(sel_flat_type) == 0) & (len(sel_town) == 0) & (len(sel_flat_model) == 0):
        df_resale = df_resale.copy()

    # Otherwise, apply the specified filters to the input DataFrame using the slice_features function.
    else:
        df_resale = slice_features(
                        df_resale, 
                        sel_flat_type=sel_flat_type, 
                        sel_town=sel_town, 
                        sel_flat_model=sel_flat_model)

    st.markdown(
            """
            I'll investigate how resale price changes with the various features:
            1. Time (month/year) - note that data is based on date of approval for the resale transactions. For March 2012 onwards, the data is based on date of registration for the resale transactions
            2. Town
            3. Flat Type
            4. Storey Range
            5. Floor Area (sqm)
            6. Flat Model
            7. Remaining Lease (years)
            """
        )

    with st.expander("Expand"):
        st.dataframe(df_resale)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        # RADIO SELECT - AGGREGATION MODE
        y_aggregation_select = st.radio(
            "Select mode of aggregation for resale price. This applies to all charts on this page",
            options=('median','mean','min','max')
        )
        st.write('You selected aggregation mode: ', y_aggregation_select)
    
    with col2:
        # RADIO SELECT - DATE LEVEL
        x_date_select = st.radio(
            "Select date level. This applies only to the first chart with time as the x-axis",
            options=('month','year')
        )
        st.write('Your selected data level is: ', x_date_select)
    with col3:
        # RADIO SELECT - VISUALISATION TYPE
        select_flat_type = st.radio(
                "Select visualisation type",
                options=("Bar","Violin/Box")
            )
        st.write(f"You selected: {select_flat_type}")
    
    # Create 2 tabs
    tab1, tab2 = st.tabs(['univariate','multivariate'])

    with tab1:
        # LINE PLOT - resale price against TIME
        # slice dataframe based on users' selected date level (month or year) and aggregate them
        df_price_date = agg_date(df_resale, x_selector=x_date_select, y_selector='resale_price')
        fig_price_date = plotly_line(df_price_date, x_date_select, y_aggregation_select)
        st.plotly_chart(fig_price_date, use_container_width=True)

        # BAR & VIOLIN PLOTS - resale price and TOWN
        # slice dataframe based on town and aggregate them
        df_price_town = agg_date(df_resale, x_selector='town', y_selector='resale_price')
        fig_price_town_bar = plotly_bar(df_price_town,x_var='town',y_var=y_aggregation_select)
        fig_price_town_violin = plotly_violin(df_resale, x_var='town')

        # BAR & VIOLIN PLOTS - resale price and FLAT TYPE
        # # slice dataframe based on  flat type and aggregate them
        df_price_flat_type = agg_date(df_resale, x_selector='flat_type', y_selector='resale_price')
        fig_price_flat_type_bar = plotly_bar(df_price_flat_type, x_var='flat_type',y_var=y_aggregation_select)
        fig_price_flat_type_violin = plotly_violin(df_resale, x_var='flat_type')
        
        # BAR & VIOLIN PLOTS - resale price and STOREY RANGE
        # slice dataframe based on storey range and aggregate them
        df_price_storey_range = agg_date(df_resale, x_selector='storey_range', y_selector='resale_price')
        fig_price_storey_range_bar = plotly_bar(df_price_storey_range, x_var='storey_range', y_var=y_aggregation_select)
        fig_price_storey_range_violin = plotly_violin(df_resale, x_var='storey_range')

        # Render BAR or VIOLIN/BOX plots depending on users' selection
        if select_flat_type == "Bar":
            st.plotly_chart(fig_price_town_bar, use_container_width=True) # render on streamlit
            st.plotly_chart(fig_price_flat_type_bar, use_container_width=True) # render on streamlit
            st.plotly_chart(fig_price_storey_range_bar, use_container_width=True) # render on streamliT
        else:
            st.plotly_chart(fig_price_town_violin, use_container_width=True) # render TOWN on streamlit
            st.plotly_chart(fig_price_flat_type_violin, use_container_width=True) # render FLAT TYPE on streamlit
            st.plotly_chart(fig_price_storey_range_violin, use_container_width=True) # render STOREY RANGE on streamlit

        # LINE PLOT - resale price and FLOOR AREA
        # slice dataframe based on floor_area_sqm and aggregate them
        df_price_area = agg_date(df_resale, x_selector='floor_area_sqm', y_selector='resale_price')
        fig_price_area = plotly_line(df_price_area, 'floor_area_sqm', y_aggregation_select)
        st.plotly_chart(fig_price_area, use_container_width=True) # render on streamlit

        # LINE PLOT - resale price against REMAINING LEASE
        # slice dataframe based on remaining lease and aggregate them
        df_price_lease = agg_date(df_resale, x_selector='remaining_lease', y_selector='resale_price')
        fig_price_lease = plotly_line(df_price_lease, 'remaining_lease',y_aggregation_select)
        st.plotly_chart(fig_price_lease, use_container_width=True) # render on streamlit

    with tab2:
        # DATAFRAME - median resale price breakdown by flat types
        with pd.option_context("display.float_format", "${:,.2f}".format):
            resale_price_table = df_resale.groupby(["town", "flat_type"]).resale_price.median().reset_index()
            resale_price_pivot = pd.pivot(resale_price_table, index="town", columns="flat_type", values="resale_price")
            # resale_table_columns = ["1 ROOM", "2 ROOM", "3 ROOM", "4 ROOM", "5 ROOM", "EXECUTIVE", "MULTI-GENERATION"]
            resale_table_columns = df_resale['flat_type'].unique()
        st.markdown("#### Median Resale Price Across Towns and Flat Types")
        st.dataframe(
            resale_price_pivot.style.background_gradient(
                    axis=None,
                    subset=resale_table_columns, 
                    vmin=resale_price_table.resale_price.min(),
                    cmap='YlOrRd'
                ).format(
                    na_rep="-",
                    precision=0,
                    thousands=","
                ).applymap(
                    lambda x: 'color: transparent; background-color: transparent' if pd.isnull(x) else ''
                ),
            use_container_width=True)


if __name__ == "__main__":
    main()
