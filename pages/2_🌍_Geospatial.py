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
def load_parquet(path_filename):
    return pd.read_parquet(path_filename)

def find_sg_coord (df):
    """
    Function to exclude non-singapore coordinates from dataframe

    Args:
        df [pandas.dataframe]: dataframe of lat and lon coordinates

    Returns:
        df [pandas.dataframe]: dataframe of Singapore lat and lon coordinates 
    """
    df = df.loc[(df['lat'] > 1.0) & (df['lat'] < 1.5)] # isolate lat values
    df = df.loc[(df['lon'] > 101) & (df['lon'] < 106)] # isolate lon values

    return df

def pydeck (df):
    INITIAL_VIEW_STATE = pdk.ViewState(
        latitude=1.25,
        longitude=103.8,
        zoom=10,
        max_zoom=16,
        pitch=45,
        bearing=0
        )
    
    hexagon = pdk.Layer(
           'HexagonLayer',
           data=df,
           get_position='[lon, lat]',
           radius=200,
           elevation_scale=4,
           elevation_range=[0, 1000],
           pickable=True,
           extruded=True,
        )
    
    scatter = pdk.Layer(
            'ScatterplotLayer',
            data=df,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
            pickable=True,
        )

    
    layers=[hexagon, scatter]

    return layers, INITIAL_VIEW_STATE

def main():
    st.set_page_config(
        page_title="Geospatial Visualisation",
        page_icon='🌍'
    )

    st.title("Geospatial Visualisation of HDB resale transactions in 2015")

    st.write("""
    
    """)

    df_resale = load_parquet(f'{artifacts_path}/{artifact_file}').drop(['Unnamed: 0','block','street_name','search_address','full_address'],axis=1)

    with st.expander("Expand to see snippet of dataframe"):
        st.dataframe(df_resale[:10000])

    df_coord = df_resale.loc[:,['Lat','Lon']]
    df_coord.columns = ['lat','lon']
    df_coord_dropna = df_coord.dropna()

    df_coord_sg = find_sg_coord(df_coord_dropna)

    st.write(
        f"""
        Of the {len(df_coord)} transactions in 2015, {(len(df_coord)-len(df_coord_dropna))} did not have valid coordinates and were dropped.

        {len(df_coord_dropna)-len(df_coord_sg)} coordinates had coordinates that are located outside of Singapore. These coordinates are also labelled as invalid and are further dropped. 

        {len(df_coord_sg)} transactions from the 2015 dataset are visualised in this page.
        """
    )

    
    # 
    st.map(df_coord_sg)

    # pydeck charts
    layers, initial_view_state = pydeck(df_coord_sg)

    token = st.secrets["token"]
    st.write()

    st.pydeck_chart(
            pdk.Deck(
                api_keys={'mapbox':token},
                initial_view_state=initial_view_state, 
                layers=layers,
                tooltip=True
            )
        )

    

if __name__ == "__main__":
    main()