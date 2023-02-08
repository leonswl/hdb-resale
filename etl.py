import pandas as pd
import yaml
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time
from math import ceil
from utility import read_concat_csv_to_df, convert_to_year_num, transform


def etl():
    """
    Function
    """

    with open("config.yml", encoding="utf-8",mode='r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.Loader)
        csv_path = cfg['etl']['csv_path']
        artifacts_path = cfg['etl']['artifacts_path']

    # read and concat csv files to a single dataframe
    df_total = read_concat_csv_to_df(csv_path)


    # apply transformation on dataset
    df_transformed = transform(df_total)

    # persist transformed artifact as parquet file
    df_transformed.to_parquet(f'{artifacts_path}/hdb_resale.parquet')

def geocode():

    """
    Function
    """
    with open("config.yml", encoding="utf-8",mode='r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.Loader)
        csv_path = cfg['geocode']['csv_path']
        csv_fname = cfg['geocode']['csv_fname']
        batch_size = cfg['geocode']['batch_size']
        artifacts_path = cfg['geocode']['artifacts_path']

    #Creating an instance of Nominatim Class
    geolocator = Nominatim(user_agent="my_request")
    
    #applying the rate limiter wrapper
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.1)
    
    start_time = time.time()

    # read input csv file
    df_2015 = pd.read_csv(f'{csv_path}/{csv_fname}')

    # apply transformation on dataset
    df_transformed = transform(df_2015)

    print(len(df_transformed))

    batch_count = ceil(len(df_transformed)/batch_size)
    batch_counter = 0
    l_index, r_index = 0, batch_size
    for i in range(batch_count):
        batch_progress = {'batch_counter': batch_counter, 'l_index': l_index}
        df_batch = df_2015[l_index:r_index] # slice dataframe according to batch size index
        batch_counter += 1
        l_index, r_index = r_index, r_index + batch_size # set new left and right index reference
        
        print(f"""
        {batch_progress}
        """)
        #Applying the method to pandas DataFrame
        df_batch['location'] = df_batch['full_address'].apply(geocode) 
        df_batch['Lat'] = df_batch['location'].apply(lambda x: x.latitude if x else None)
        df_batch['Lon'] = df_batch['location'].apply(lambda x: x.longitude if x else None)

        # persist each batch as csv
        df_batch.to_csv(f'{artifacts_path}/df_2015_{batch_counter-1}.csv')

    end_time = time.time()

    time_taken = (end_time - start_time)/60
    print(time_taken)


if __name__ == "__main__":
    # etl()
    geocode()