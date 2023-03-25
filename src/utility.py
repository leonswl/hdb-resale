import pandas as pd
import numpy as np
import glob
import streamlit as st
import plotly.express as px

def read_concat_csv_to_df(path):
    """
    Function to read all csv in a folder and concat them into a single pandas dataframe

    Args:
        path [string]: path where csv files are located

    Returns:
        df_total [dataframe]: pandas dataframe after concat

    """
    # initialise empty list
    df_lst = []

    # iterate through folder of csv
    for fname in glob.glob(path): 
        df_raw = pd.read_csv(fname) # read csv into pandas df
        df_lst.append(df_raw) # append df into list

    return pd.concat(df_lst)


def transform(df_bef: pd.DataFrame) -> pd.DataFrame:
    """
    Function to apply transformation to the datasets

    Args:
        df_bef [dataframe]: pandas dataframe that require transformation

    Returns:
        df_aft [dataframe]: pandas dataframe after applying transformation
    
    """
    list_cols = ['remaining_lease','block','full_address','street_name','year','resale_price','flat_type','lease_commence_date']
    result = any(item in df_bef.columns for item in list_cols)

    if result is True:

        # convert string values of `remaining_lease` into years, rounded off to the nearest integer
        df_bef['remaining_lease'] = df_bef['remaining_lease'].apply(lambda x: convert_to_year_num(x) if isinstance(x,str) else x)

        # combine block and street name as new address column and drop these columns
        df_bef['full_address'] = df_bef['block'] + ' ' + df_bef['street_name']
        df_bef['search_address'] = df_bef['block'] + '+' + df_bef['street_name'].str.replace(' ', '+') + '+SINGAPORE'    

        # drop irrelevant columns
        df_aft = df_bef.drop(['block','street_name'],axis=1)

        # create year column
        df_aft['year'] = df_aft['month'].apply(lambda x: int(x.split('-')[0]))

        # convert resale_price column to integer
        df_aft['resale_price'] = df_aft['resale_price'].apply(lambda x: int(x))

        # clean value
        df_aft['flat_type'] = df_aft['flat_type'].replace('MULTI GENERATION','MULTI-GENERATION')

        df_aft['remaining_lease'] = df_aft['remaining_lease'].fillna(99-(df_aft['year']-df_aft['lease_commence_date']))

    else:
        print("dataframe does not have the necessary columns")

    return df_aft

def convert_to_year_num(val):
    """
    Function to convert years in string values to int, rounded off to the nearest integer

    Args:
        val [string]: string value of years and months. E.g. '68 years 03 months', '56 years'

    Returns:
        year_num (int): years rounded off to the nearest integer

    """

    # Split the string into a list of words
    str_lst = val.split(' ')

    # Check if the string only contains a year value (e.g. '56 years')
    if len(str_lst) <= 2:
        # Convert the year value to an integer and return it
        return int(str_lst[0],0)
    
    # If the string contains a year and month value (e.g. '68 years 03 months'),
    # convert the year value to an integer and add the fractional value of months
    year = int(str_lst[0])
    return int(round(year + int(str_lst[2]) / 12, 0))


def apply_geocode (df_geocode, address_field):
    """
    Function to apply geocode on addresses

    Args:
        df_geocode [dataframe]: pandas dataframe with address
        address_field [string]: name of dataframe column containing address
    
    Returns:
        df_geocode [dataframe]: pandas dataframe with latitude and longitude
    """
    from geopy.geocoders import Nominatim
    from geopy.extra.rate_limiter import RateLimiter

    #Creating an instance of Nominatim Class
    geolocator = Nominatim(user_agent="my_request")
    
    #applying the rate limiter wrapper
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    if 'location' not in df_geocode.columns:
        df_geocode['location'] = df_geocode['search_address'].apply(geocode)
    else:
        df_geocode['location'] = df_geocode['search_address'].apply(geocode)
        print("Geocode field is named as location1")
        
    return df_geocode



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



def slice_features(df: pd.DataFrame, sel_flat_type: list, sel_town: list, sel_flat_model: list) -> pd.DataFrame:
    """
    Returns a filtered pandas DataFrame containing only the rows with flat types specified in sel_flat_type.

    Args:
        df (pandas.DataFrame): Input DataFrame to filter.
        sel_flat_type (list): List of flat types to filter the DataFrame.
        sel_town (list): List of towns to filter the DataFrame.
        sel_flat_model (list): List of flat models to filter the DataFrame.

    Returns:
        pandas.DataFrame: Filtered DataFrame containing only the specified flat types, towns and flat models.
    """
    
    # Filter the input DataFrame by selecting rows where the 'flat_type' column value is in the list of selected flat types.
    df_flat_type = df.loc[df['flat_type'].isin(sel_flat_type)]
    
    # Filter the df_flat_type by selecting rows where the 'town' column value is in the list of selected towns.
    df_town = df_flat_type.loc[df_flat_type['town'].isin(sel_town)]
    
    # Filter the df_town by selecting rows where the 'flat_model' column value is in the list of selected flat models.
    df_flat_model = df_town.loc[df_town['flat_model'].isin(sel_flat_model)]
    
    # Return the filtered DataFrame.
    return df_flat_model

@st.cache_data(ttl=300)
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

#
@st.cache_data(ttl=300)
def plotly_violin(df, x_var):
    """Plot a violin plot of resale prices against a specified x-variable.
    
    Args:
        df (pandas.DataFrame): DataFrame containing the resale prices and the specified x-variable.
        x_var (str): Name of the x-variable to plot against.
        
    Returns:
        fig_violin (plotly.graph_objs._figure.Figure): Plotly figure object of the violin plot.
    """
    # Create a violin plot using Plotly
    fig_violin = px.violin(
        df,                             # Dataframe to use for plotting
        y='resale_price',               # Column containing the resale prices
        x=x_var,                        # Column containing the specified x-variable
        color=x_var,                    # Color data points by the specified x-variable
        title=f"Resale Price and {x_var.replace('_',' ').title()}",    # Title of the plot
        box=True                        # Show a box plot on top of the violin plot
    )
    
    # Update the layout of the plot with axis titles and legend parameters
    fig_violin = fig_violin.update_layout(
        xaxis_title=x_var.replace('_',' ').title(),         # Title of the x-axis
        yaxis_title="Resale Price (S$)",                     # Title of the y-axis
        legend={
            "orientation": "h",                             # Orientation of the legend
            "y": 1.15,                                      # Position of the legend on the y-axis
            # "x": 0.2,                                      # Position of the legend on the x-axis
            "title": None                                   # Title of the legend (set to None to remove)
        }
    )
    
    return fig_violin    # Return the plotly figure object

@st.cache_data(ttl=300)
def plotly_bar (df,x_var,y_var):
    fig_bar = px.bar(
        df, 
        x=x_var,
        y=y_var,
        title=f"{y_var.title()} Resale Price in each {x_var.replace('_',' ').title()}",
        text_auto=True
    ).update_layout(
        xaxis={'categoryorder':'total descending'},
        xaxis_title=x_var.replace('_',' ').title(),
        yaxis_title = f"{y_var.title()} Resale Price (S$)"
    )
    return fig_bar

@st.cache_data(ttl=300)
def plotly_line(df,x_var, y_var):
            fig_line = px.line(
                df, 
                x=x_var, 
                y=y_var, 
                title=f"{y_var.title()} Resale Price against {x_var.replace('_',' ').title()}"
            ).update_layout(
                xaxis_title=x_var.replace('_',' ').title(),
                yaxis_title = f"{y_var.title()} Resale Price (S$)"
                )

            return fig_line