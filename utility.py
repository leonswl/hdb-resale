import pandas as pd
import numpy as np
import glob


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

    df_total = pd.concat(df_lst) # concat list of dfs into a single df

    return df_total


def transform(df_bef: pd.DataFrame) -> pd.DataFrame:
    """
    Function to apply transformation to the datasets

    Args:
        df_bef [dataframe]: pandas dataframe that require transformation

    Returns:
        df_aft [dataframe]: pandas dataframe after applying transformation
    
    """
    list_cols = ['remaining_lease','block','full_address','street_name']
    result = any(item in df_bef.columns for item in list_cols)

    if result is True:

        # convert string values of `remaining_lease` into years, rounded off to the nearest integer
        df_bef['remaining_lease'] = df_bef['remaining_lease'].apply(lambda x: convert_to_year_num(x) if isinstance(x,str) else x)

        # combine block and street name as new address column and drop these columns
        df_bef['full_address'] = df_bef['block'] + ' ' + df_bef['street_name']
        df_bef['search_address'] = df_bef['block'] + '+' + df_bef['street_name'].str.replace(' ', '+') + '+SINGAPORE'    

        # drop irrelevant columns
        df_aft = df_bef.drop(['block','street_name'],axis=1)

    else:
        print("dataframe does not have the necessary columns")

    return df_aft

def convert_to_year_num (val):
    """
    Function to convert years in string values to int, rounded off to the nearest integer

    Args:
        val [string]: string value of years and months. E.g. '68 years 03 months', '56 years'

    Returns:
        year_num (int): years rounded off to the nearest integer

    """
    str_lst = val.split(' ')
    # if there are more than 2 values in the list, i.e. have both years and months
    if len(str_lst) > 2: 
        year = int(str_lst[0])
        month = int(str_lst[2])
        year_num = int(round(year + month/12,0))
    # only years value 
    else:
        year_num = int(str_lst[0],0)
    return year_num


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