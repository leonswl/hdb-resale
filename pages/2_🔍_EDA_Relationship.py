# Script for second page of Streamlit on EDA
import pandas as pd
import numpy as np
import yaml
import streamlit as st
import plotly.express as px

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

# 
@st.cache_data(ttl=300)
def agg_date(df, x_selector, y_selector):
    """Aggregate the input DataFrame `df` by a given `date_level_selector`.

    Args:
        df (pd.DataFrame): Input DataFrame to be aggregated.
        date_level_selector (str): Column name to group the DataFrame by.

    Returns:
        pd.DataFrame: Aggregated DataFrame with minimum, maximum, mean and median resale prices
    """
    
    # Group the DataFrame by the given date_level_selector column
    # and aggregate the resale_price column using different functions
    df_agg = pd.DataFrame(df
                .groupby(by=[x_selector])
                .agg(
                    min=pd.NamedAgg(column=y_selector, aggfunc='min'),
                    max=pd.NamedAgg(column=y_selector, aggfunc='max'),
                    mean=pd.NamedAgg(column=y_selector, aggfunc=lambda x: int(np.mean(x))),
                    median=pd.NamedAgg(column=y_selector, aggfunc=lambda x: int(np.median(x)))
                    )
                ).reset_index()
    
    return df_agg


def slice_year_range (df, start_year, end_year):
    """
    Filters a pandas DataFrame to include only rows where the value of 'year' column is greater than 
    the 'start_year' variable and less than the 'end_year' variable.

    Args:
    - df: pandas DataFrame with a column named 'year'

    Returns:
    - pandas DataFrame with only rows where the 'year' value is greater than 'start_year' and less than 'end_year'
    """
    
    # Filter the DataFrame to only include rows where the 'year' value is greater than 'start_year'
    # and less than 'end_year'
    return df.loc[(df['year']>start_year) & (df['year']<end_year)]

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
            value=(date_range_lst.min(),date_range_lst.max())
        )
        st.write('You selected year range between', start_year, 'and', end_year)

        # RADIO SELECT - AGGREGATION MODE
        y_aggregation_select = st.radio(
            "Select mode of aggregation for resale price. This applies to all charts on this page",
            options=('mean','median','min','max')
        )
        st.write('You selected aggregation mode: ', y_aggregation_select)

        # RADIO SELECT - DATE LEVEL
        x_date_select = st.radio(
            "Select date level. This applies only to the first chart with time as the x-axis",
            options=('month','year')
        )
        st.write('Your selected data level is: ', x_date_select)

    

    # slice year range based on user's selected range
    df_resale = slice_year_range(df_load, start_year=start_year, end_year=end_year)
    df_resale.drop(['full_address','search_address','lease_commence_date'],axis=1,inplace=True)

    col1, col2 = st.columns([2,3])

    with col1:
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
    
    with col2:
        st.metric('value','value')

    with st.expander("Expand"):
        st.dataframe(df_resale)
    # LINE PLOT - resale price against TIME
    # slice dataframe based on users' selected date level (month or year) and aggregate them
    df_price_date = agg_date(df_resale, x_selector=x_date_select, y_selector='resale_price')
    fig_price_date = px.line(
                        df_price_date, 
                        x=x_date_select, 
                        y=y_aggregation_select, 
                        title='Resale Price against Time')
    st.plotly_chart(fig_price_date, use_container_width=True)

    # BAR PLOT - resale price and TOWN
    # slice dataframe based on town and aggregate them
    df_price_town = agg_date(df_resale, x_selector='town', y_selector='resale_price')

    fig_price_town = px.bar(
                    df_price_town, 
                    x='town',
                    y=y_aggregation_select,
                    title=f'{y_aggregation_select.title()} Resale Price in each Town',
                    text_auto=True).update_layout(xaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig_price_town, use_container_width=True) # render on streamlit

    # BAR PLOT - resale price and FLAT TYPE
    # slice dataframe based on  flat type and aggregate them
    df_price_town = agg_date(df_resale, x_selector='flat_type', y_selector='resale_price')

    fig_price_town = px.bar(
                    df_price_town, 
                    x='flat_type',
                    y=y_aggregation_select,
                    title=f'{y_aggregation_select.title()} Resale Price in each Flat Type',
                    text_auto=True).update_layout(xaxis={'categoryorder':'total descending'})
    st.plotly_chart(fig_price_town, use_container_width=True) # render on streamlit


    # BAR PLOT - resale price and STOREY RANGE
    # slice dataframe based on storey range and aggregate them
    df_price_town = agg_date(df_resale, x_selector='storey_range', y_selector='resale_price')
    fig_price_town = px.bar(
                    df_price_town, 
                    x='storey_range',
                    y=y_aggregation_select,
                    title=f'{y_aggregation_select.title()} Resale Price in each Storey Range',
                    text_auto=True).update_layout(xaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_price_town, use_container_width=True) # render on streamliT

    # LINE PLOT - resale price and FLOOR AREA
    # slice dataframe based on floor_area_sqm and aggregate them
    df_price_area = agg_date(df_resale, x_selector='floor_area_sqm', y_selector='resale_price')
    fig_price_area = px.line(
                        df_price_area, x='floor_area_sqm', 
                        y=y_aggregation_select, 
                        title='Resale Price against Floor Area (sqm)') # generate figure
    st.plotly_chart(fig_price_area, use_container_width=True) # render on streamlit


    # LINE PLOT - resale price against REMAINING LEASE
    # slice dataframe based on remaining lease and aggregate them
    df_price_lease = agg_date(df_resale, x_selector='remaining_lease', y_selector='resale_price')
    fig_price_lease = px.line(df_price_lease, x='remaining_lease', y=y_aggregation_select, title='Resale Price against Remaining Lease') # generate figure
    st.plotly_chart(fig_price_lease, use_container_width=True) # render on streamlit




if __name__ == "__main__":
    main()
