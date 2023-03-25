import pandas as pd
import yaml
from .utility import read_concat_csv_to_df, transform

def prepare():
    """
    Load CSV files, apply a transformation, and save the result as a parquet file.
    """

    # Load configuration settings from YAML file
    with open("config.yml", encoding="utf-8",mode='r') as ymlfile:
        cfg = yaml.load(ymlfile, Loader=yaml.Loader)

        # Get the paths for the input and output files from the configuration settings
        csv_path = cfg['etl']['csv_path']
        artifacts_path = cfg['etl']['artifacts_path']

    # read and concat csv files to a single dataframe
    df_total = read_concat_csv_to_df(csv_path)

    # Apply a transformation to the dataset using the `transform()` function
    df_transformed = transform(df_total)

    # persist transformed artifact as parquet file
    df_transformed.to_parquet(f'{artifacts_path}/hdb_resale.parquet')

    print(f"Successfully persisted dataset in {artifacts_path}/hdb_resale.parquet")

if __name__ == "__main__":
    # Call the `prepare()` function when this script is run as the main program
    prepare()
    