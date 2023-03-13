# Script for first page of Streamlit on EDA
import pandas as pd
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

def plot_town_transacts(df):
    """
    Plots a bar chart of the number of transactions in each town.

    Args:
        df (pandas.DataFrame): A pandas DataFrame containing the data to be plotted. 
            Must have a 'town' column.

    Returns:
        plotly.graph_objs._figure.Figure: A plotly bar chart figure object.
    """

    # Check if 'town' column exists in DataFrame
    if 'town' in df.columns:
        # Create a DataFrame grouped by town and count the number of transactions
        df_town = pd.DataFrame(df.groupby(['town']).town.count())
        # Rename the column to 'num_transactions'
        df_town.columns = ['num_transactions']
        # Sort the DataFrame by number of transactions in descending order
        df_town = df_town.sort_values(by=['num_transactions'], ascending=False).reset_index()

        # Create a bar chart using Plotly Express
        fig = px.bar(df_town, x='town', y='num_transactions', text_auto=True, 
                    title="Number of Transactions in each Town")
        return fig

    else:
        # If 'town' column is not present in DataFrame, print an error message
        st.write("'town' attribute is not present in the data set")

def plot_flat_type_transacts(df):
    """
    Plots a bar chart of the number of transactions for each type of flat.

    Args:
        df (pandas.DataFrame): A pandas DataFrame containing the data to be plotted. 
            Must have a 'flat_type' column.

    Returns:
        plotly.graph_objs._figure.Figure: A plotly bar chart figure object.
    """

    # Check if 'flat_type' column exists in DataFrame
    if 'flat_type' in df.columns:
        # Create a DataFrame grouped by flat_type and count the number of transactions
        df_flat_type = pd.DataFrame(df.groupby(['flat_type']).flat_type.count())
        # Rename the column to 'num_transactions'
        df_flat_type.columns = ['num_transactions']
        # Sort the DataFrame by number of transactions in descending order
        df_flat_type = df_flat_type.sort_values(by='num_transactions', ascending=False).reset_index()

        # Create a bar chart using Plotly Express
        fig_flat_type = px.bar(df_flat_type, x='flat_type', y='num_transactions', text_auto=True, title="Number of Transactions for each type of flat")
        return fig_flat_type
        
    else:
        # If 'flat_type' column is not present in DataFrame, print an error message
        st.write("'flat_type' attribute is not present in the data set")

def plot_storey_transacts(df):
    """
    Plots a bar chart of the number of transactions in each storey range.

    Args:
        df (pandas.DataFrame): A pandas DataFrame containing the data to be plotted. 
            Must have a 'storey_range' column.

    Returns:
        plotly.graph_objs._figure.Figure: A plotly bar chart figure object.
    """

    # Check if 'storey_range' column exists in DataFrame
    if 'storey_range' in df.columns:
        # Create a DataFrame grouped by storey range and count the number of transactions
        df_storey = pd.DataFrame(df.groupby(['storey_range']).storey_range.count())
        # Rename the column to 'num_transactions'
        df_storey.columns = ['num_transactions']
        # Sort the DataFrame by number of transactions in descending order
        df_storey = df_storey.sort_values(by=['num_transactions'], ascending=False).reset_index()

        # Create a bar chart using Plotly Express
        fig = px.bar(df_storey, x='storey_range', y='num_transactions', text_auto=True, 
                     title="Number of Transactions in each Storey Range")
        return fig

    else:
        # If 'storey_range' column is not present in DataFrame, print an error message
        st.write("'storey_range' attribute is not present in the data set")

def plot_month_transacts(df):
    """
    Plots a bar chart of the number of transactions in each storey range.

    Args:
        df (pandas.DataFrame): A pandas DataFrame containing the data to be plotted. 
            Must have a 'storey_range' column.

    Returns:
        plotly.graph_objs._figure.Figure: A plotly bar chart figure object.
    """

    # Check if 'storey_range' column exists in DataFrame
    if 'month' in df.columns:
        # Create a DataFrame grouped by storey range and count the number of transactions
        df_month = pd.DataFrame(df.groupby(['month']).month.count())
        # Rename the column to 'num_transactions'
        df_month.columns = ['num_transactions']
        # Sort the DataFrame by number of transactions in descending order
        df_month = df_month.sort_values(by=['num_transactions'], ascending=False).reset_index()

        # Create a bar chart using Plotly Express
        fig = px.bar(df_month, x='month', y='num_transactions', text_auto=True, title="Number of Transactions in each Month")
        return fig

    else:
        # If 'storey_range' column is not present in DataFrame, print an error message
        st.write("'storey_range' attribute is not present in the data set")


def main():
    """
    First page of Streamlit app to render EDA visualisations
    """

    st.set_page_config(
        page_title="Second page of streamlit app",
        page_icon='🏠',
        layout="wide",
    )

    st.title("Exploratory Data Analysis of HDB Resale Transactions")

    # load data artifact
    df_load = load_parquet(f'{artifacts_path}/hdb_resale.parquet')

    # SIDEBAR
    with st.sidebar:
        date_range_lst = df_load.year.unique()
        date_range_lst.sort()

        start_year, end_year = st.select_slider(
            "Select range of years",
            options=date_range_lst,
            value=(date_range_lst.min(),date_range_lst.max())
        )
        st.write('You selected year range between', start_year, 'and', end_year)
    # END - SIDEBAR

    # METRICS
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions",len(df_load))
    col2.metric("Highest Transaction", f"S${int(max(df_load['resale_price']))}")
    col3.metric("Most Popular Town","Tampines")
    # END - METRICS

    st.write("""
    I’ll perform initial investigations of the dataset to discover any patterns and anomalies, and also check hypothesis and form hypothesis. 
    """)
    
    # slice year range based on user's selected range
    df_resale = slice_year_range(df_load, start_year=start_year, end_year=end_year)

    # DATAFRAME SNIPPET
    with st.expander("Expand to see snippet of dataframe"):
        st.dataframe(df_resale[:10000])


    # BAR PLOT - Number of Transactions in each town
    fig_town = plot_town_transacts(df_resale)
    # render plotly figure on streamlit
    st.plotly_chart(fig_town, use_container_width=True)

    # BAR PLOT - Number of transactions in each flat type  
    fig_flat_type = plot_flat_type_transacts(df_resale)
    # render plotly figure on streamlit
    st.plotly_chart(fig_flat_type, use_container_width=True)

    # BAR PLOT - Number of Transactions in each storey range
    fig_storey_range = plot_storey_transacts(df_resale)
    # render plotly figure on streamlit
    st.plotly_chart(fig_storey_range, use_container_width=True)

    # LINE PLOT - Number of Transactions over time
    fig_month = plot_month_transacts(df_resale)
    # render plotly figure on streamlit
    st.plotly_chart(fig_month, use_container_width=True)

if __name__ == "__main__":
    main()
