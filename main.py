import pandas as pd
import yaml
import time
import streamlit as st
from PIL import Image

def main():
    """
    Main streamlit app for rendering analytical visualisations
    """

    st.set_page_config(
        page_title="Main page of streamlit app",
        page_icon=""    
    )

    with st.sidebar:
        st.success("Select a demo above")
        st.write("This dashboard is created by [Leon Sun](https://github.com/leonswl). The source code for this project is published in this [GitHub Repository](https://github.com/leonswl/hdb-resale).")

    # title
    st.title("HDB Resale Transactions (1990-2023)")

    image = Image.open("assets/jiachen-lin-AIk_5-M9Uho-unsplash.jpg")
    st.image(
        image,
        caption="Photo by Jiachen Lin on Unsplash"
    )
    
    st.markdown(
        """
        Using streamlit, an open-source framework to render visualisations in a dashboard.
        """
    )

    # Main Content
    st.markdown(
        """

        ## Objectives
        1.	Exploratory Data Analysis (EDA) – I’ll perform initial investigations of the dataset to discover any patterns and anomalies.
        2.	How does resale price vary throughout Singapore, with respect to other relevant factors such as flat type, floor area, number of levels etc.?
        3.	Can these information help in choosing a resale flat? 
        
        **Visualisations**
        - Most charts are plotted using [Plotly Open Source Graphing Library for Python](https://plotly.com/python/)
        - Geospatial charts are plotted using [PyDeck](https://pydeck.gl/) - layers are rendered from the [deck.gl layers catalog](https://deck.gl/docs/api-reference/layers)
        - Map tiles used to render spatial plots are provided by Mapbox. My personal token registered with mapbox is used for this project.
            - For replication of this project locally, please register and provide your own token and store it in your local streamlit folder `/.streamlit/secrets.toml`

        **Datasets**
        - Original Dataset: [HDB Resale Flat Prices](https://data.gov.sg/dataset/resale-flat-prices)
        - Cleaned Dataset: [1990-2023 Dataset](https://github.com/leonswl/hdb-resale/blob/main/artifacts/hdb_resale.parquet)
        - 2015 Transactions with Coordinates Dataset: [2015 Geocoded Resale Transactions](artifacts/2015_geocoded.parquet)
        """
    )

    with st.expander("References - Click to expand "):
        st.markdown(
            """
            1. Kaggle Dataset: [Singapore HDB Flat Resale Prices (1990-2020)](https://www.kaggle.com/datasets/teyang/singapore-hdb-flat-resale-prices-19902020)
            2. Medium Article: [Data-Driven Approach to Understanding HDB Resale Prices in Singapore](https://towardsdatascience.com/data-driven-approach-to-understanding-hdb-resale-prices-in-singapore-31c3beecfd97)
            3. Image Credit
                - Creator: User Jiachen Lin from Unsplash
                - URL: https://unsplash.com/@jiachenlin?utm_source=unsplash&utm_medium=referral&utm_content=creditCopyText
  
            """
        )


if __name__ == "__main__":
    main()