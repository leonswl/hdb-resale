# Script for geospatial analysis page Streamlit
import pandas as pd
import yaml
import streamlit as st
# import plotly.express as px
import pydeck as pdk

with open("config.yml", encoding="utf-8", mode='r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.Loader)
    artifacts_path = cfg['eda']['artifacts_path']
    artifact_file = cfg['geospatial']['artifact_file']


# cache data to avoid reloading data
@st.cache_data(ttl=300)
def load_clean_parquet(path_filename):
    """
    Load a parquet file into a Pandas DataFrame, rename the columns 'Lat' and 'Lon' to 'lat' and 'lon' respectively, 
    and drop any rows with missing values.
    
    Parameters:
    path_filename (str): The path and filename of the parquet file to load.
    
    Returns:
    Pandas DataFrame: A cleaned DataFrame with non-missing values and renamed columns.
    """

    # Load the parquet file into a DataFrame using Pandas' read_parquet function
    df = pd.read_parquet(path_filename).drop(['Unnamed: 0','block','street_name','search_address','full_address'],axis=1)
    
    # Rename the 'Lat' and 'Lon' columns to 'lat' and 'lon' respectively
    df_coord = df.rename(columns={'Lat':'lat','Lon':'lon'})
    
    # Drop any rows with missing values
    df_coord_dropna = df_coord.dropna()

    # create year column
    df_coord_dropna['year'] = df_coord_dropna['month'].apply(lambda x: int(x.split('-')[0]))

    # Return the cleaned DataFrame
    return df_coord_dropna


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

def find_sg_coord(df):
    """
    Function to exclude non-singapore coordinates from dataframe

    Args:
        df [pandas.dataframe]: dataframe of lat and lon coordinates

    Returns:
        df [pandas.dataframe]: dataframe of Singapore lat and lon coordinates 
    """
    df = df.loc[(df['lat'] > 1.0) & (df['lat'] < 1.5)] # isolate lat values
    df = df.loc[(df['lon'] > 101) & (df['lon'] < 106)] # isolate lon values

    df['resale_price_thousands'] = df['resale_price'] / 1000

    return df

def select_elevation_var(input_elevation_var):
    """
    Given a string representing an elevation variable, returns a standardized version of the variable name.

    Args:
    input_elevation_var (str): A string representing an elevation variable. Valid options are:
                              'Resale Price', 'Floor Area (sqm)', and 'Remaining Lease'.
    
    Returns:
    elevation_var (str): A standardized version of the elevation variable name.
                         For 'Resale Price', returns 'resale_price_thousands'.
                         For 'Floor Area (sqm)', returns 'floor_area_sqm'.
                         For 'Remaining Lease', returns 'remaining_lease'.
    """
    
    # Check which elevation variable was passed in and assign the corresponding standardized variable name to elevation_var.
    if input_elevation_var == 'Resale Price':
        elevation_var = 'resale_price_thousands'
    elif input_elevation_var == 'Floor Area (sqm)':
        elevation_var = 'floor_area_sqm'
    elif input_elevation_var == 'Remaining Lease':
        elevation_var = 'remaining_lease'
    
    # Return the standardized variable name.
    return elevation_var

def pydeck (df, elevation_var):
    INITIAL_VIEW_STATE = pdk.ViewState(
        latitude=1.25,
        longitude=103.8,
        zoom=10,
        max_zoom=16,
        pitch=45,
        bearing=0
        )
    
    column = pdk.Layer(
           'ColumnLayer',
           data=df,
           get_position='[lon, lat]',
           get_elevation=elevation_var,
           radius=50,
           elevation_scale=10,
           elevation_range=[0, 200],
           pickable=True,
           extruded=True,
           auto_highlight=True,
           get_fill_color=[180, 0, 200, 140]
        )
    
    scatter = pdk.Layer(
            'ScatterplotLayer',
            data=df,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=70,
            pickable=True,
        )

    layers=[scatter, column]

    return layers, INITIAL_VIEW_STATE

def main():
    st.set_page_config(
        page_title="Geospatial Visualisation",
        page_icon='🌍'
    )

    # Load and prepare dataset for geospatial visualisation
    df_load = load_clean_parquet(f'{artifacts_path}/{artifact_file}')

    #  include only sg coordinates
    df_coord_sg = find_sg_coord(df_load)

    # SIDEBAR
    with st.sidebar:
        input_elevation_var = st.selectbox(
            "Select field for Elevation",
            ('Resale Price','Floor Area (sqm)','Remaining Lease')
        )

        # MULTISELECT - FLAT TYPE
        flat_type_fields = df_coord_sg['flat_type'].unique()
        sel_flat_type = st.multiselect(
            "Select flat types",
            options=flat_type_fields
                )

        # MULTISELECT - TOWN
        town_fields = df_coord_sg['town'].unique()
        sel_town = st.multiselect(
                    "Select town",
                    options=town_fields
                )
        
        # MULTISELECT - FLAT MODEL
        flat_model_fields = df_coord_sg['flat_model'].unique()
        sel_flat_model = st.multiselect(
                    "Select flat model",
                    options=flat_model_fields
        )
    # END - SIDEBAR 

    # slice year range based on
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
        df_resale = df_coord_sg


    # Otherwise, apply the specified filters to the input DataFrame using the slice_features function.
    else:
        df_resale = slice_features(
                        df_coord_sg, 
                        sel_flat_type=sel_flat_type, 
                        sel_town=sel_town, 
                        sel_flat_model=sel_flat_model)

    # MAIN PAGE

    st.title("Geospatial Visualisation of HDB resale transactions in 2015")
    
    # Streamlit Map
    st.markdown(
        """
        ### Scatter Map of Transactions using Streamlit Map

        This geospatial chart provides a simple 2-dimensional view of transactions scattered all over Singapore. Clusters can be identified easily on where these transactions took place. 
        """
    )

    st.map(df_resale[["lat","lon"]])

    st.markdown(
        """
        ### Columnar Map of Transactions using PyDeck

        This geospatial chart consist of 3 layers. At the base, a view state of geographical map is laid out. Layered on top is a secondary layer of scatter plot (in red) with the transactions. A primary columnar layer (in purple) covers the rest, with the elevationa attribute based on the selected field in the left sidebar.

        Default field is **Resale Price**.

        """
    )

    # pydeck charts
    elevation_var = select_elevation_var(input_elevation_var)
    layers, initial_view_state = pydeck(df_resale, elevation_var=elevation_var)

    token = st.secrets["token"]

    st.pydeck_chart(
            pdk.Deck(
                api_keys={'mapbox':token},
                initial_view_state=initial_view_state, 
                layers=layers,
                tooltip={
                    'html': '<b>Flat Model:</b> {flat_model} <br> <b>Flat Type: </b> {flat_type} <br> <b>Town: </b> {town} <br> <b>Resale Price: S$</b> {resale_price} <br> <b>Storey Range: </b> {storey_range} <br> <b>Floor Area (sqm): </b> {floor_area_sqm} <br> <b>Remaining Lease :</b> {remaining_lease}', 
                    'style': {
                        'color': 'white'
                    }
                }
            )
        )
    
    
    with st.expander("Expand to see more about the data"):
        st.markdown(
            """
            ### Dataframe Snippet
            """
        )
        st.dataframe(df_resale[:10000])


        # st.markdown(
        #     f"""
        #     ### Preparing the data: 
        #     Of the {len(df_resale)} transactions in 2015 that had coordinates, {len(df_resale)-len(df_coord_sg)} coordinates had coordinates that are located outside of Singapore. These coordinates are also labelled as invalid and are further dropped. 

        #     {len(df_coord_sg)} transactions from the 2015 dataset are visualised in this page.
        #     """
        # )

    

if __name__ == "__main__":
    main()