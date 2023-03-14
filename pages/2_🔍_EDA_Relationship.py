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

        # 
        aggregation_select = st.radio(
            "Select mode of aggregation",
            options=('min','max','mean')
        )
        st.write('You selected aggregation mode', aggregation_select)

    

    st.write("""
    I’ll investigate more about the relationships between resale price and other factors. 
    """)


    # slice year range based on user's selected range
    df_resale = slice_year_range(df_load, start_year=start_year, end_year=end_year)

    df_agg_month = pd.DataFrame(df_resale.groupby(by=['month'])
                                 .agg(
                                    min=pd.NamedAgg(column='resale_price',aggfunc='min'),
                                    max=pd.NamedAgg(column='resale_price',aggfunc='max'),
                                    mean=pd.NamedAgg(column='resale_price',
                                    aggfunc=lambda x: int(np.mean(x)))
                                    )
                                ).reset_index()


    st.dataframe(df_agg_month[:1000])


    fig_line = px.line(df_agg_month, x="month", y=aggregation_select, title='')
    st.plotly_chart(fig_line, use_container_width=True)




if __name__ == "__main__":
    main()
