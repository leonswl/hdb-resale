import yaml
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time
from math import ceil
from src.utility import transform, read_concat_csv_to_df


def geocode():
    """
    Function to perform geocoding on a CSV file and output the results in batches as separate CSV files

    Inputs:
    None

    Outputs:
    None
    """
    # Load configuration settings from YAML file
    with open("config.yml", encoding="utf-8",mode='r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.Loader)
        csv_path = cfg['geocode']['csv_path']
        csv_fname = cfg['geocode']['csv_fname']
        batch_size = cfg['geocode']['batch_size']
        artifacts_path = cfg['geocode']['artifacts_path']

    # Creating an instance of the Nominatim class from the geopy library for geocoding
    geolocator = Nominatim(user_agent="my_request")

    # Applying the rate limiter wrapper from the geopy library to prevent overloading the geocoding API
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.1)

    start_time = time.time()

    # Read input CSV file using pandas
    df_2015 = pd.read_csv(f'{csv_path}/{csv_fname}')

    # Apply data transformation using a function from an imported utility module
    df_transformed = transform(df_2015)

    # Print the number of rows in the transformed data frame
    print(len(df_transformed))

    # Calculate the number of batches needed based on the batch size and the length of the data frame
    batch_count = ceil(len(df_transformed)/batch_size)
    batch_counter = 0
    l_index, r_index = 0, batch_size

    # Loop through each batch of data
    for _ in range(batch_count):
        # Create a dictionary to track progress and batch information
        batch_progress = {'batch_counter': batch_counter, 'l_index': l_index}

        # Slice the data frame to create the current batch
        df_batch = df_2015[l_index:r_index]

        # Increment the batch counter and update the left and right index references for the next batch
        batch_counter += 1
        l_index, r_index = r_index, r_index + batch_size

        # Print progress information for the current batch
        print(f"""
        {batch_progress}
        """)

        # Apply the geocoding method to the 'full_address' column of the batch data frame
        df_batch['location'] = df_batch['full_address'].apply(geocode)
        df_batch['Lat'] = df_batch['location'].apply(lambda x: x.latitude if x else None)
        df_batch['Lon'] = df_batch['location'].apply(lambda x: x.longitude if x else None)

        # Persist the current batch as a separate CSV file
        df_batch.to_csv(f'{artifacts_path}/df_2015_{batch_counter-1}.csv')

    end_time = time.time()

    # Print the total time taken to process all batches
    time_taken = (end_time - start_time)/60
    print(time_taken)

def geocode_combine():
    """Combine geocode files and save the result as a parquet file."""

    # Load configuration settings from YAML file
    with open("config.yml", encoding="utf-8", mode='r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.Loader)

        # Get the paths for the input and output files from the configuration settings
        geocode_files_path = cfg['geocode_combine']['geocode_files_path']
        artifacts_path = cfg['geocode_combine']['artifacts_path']

    # Read and concatenate CSV files into a Pandas DataFrame
    df_geocode_combine = read_concat_csv_to_df(geocode_files_path)

    # Write the resulting DataFrame to a parquet file
    df_geocode_combine.to_parquet(f'{artifacts_path}/2015_geocoded.parquet')

if __name__ == "__main__":
    geocode()
    geocode_combine()
