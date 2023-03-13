import pandas as pd
import yaml
import streamlit as st

def main():
    """
    Main streamlit app for rendering analytical visualisations
    """

    st.set_page_config(
        page_title="Main page of streamlit app",
        page_icon=""
    )

    st.sidebar.success("Select a demo above")

    # title
    st.title("SD6105 - Data visualisation on HDB Resale Transactions")

    st.markdown(
        """
        Using streamlit, an open-source framework to render visualisations in a dashboard.
        """
    )

    # Main Content
    st.markdown(
        """

        ## Objectives
        1.	Exploratory Data Analysis (EDA) – I’ll perform initial investigations of the dataset to discover any patterns and anomalies, and also check hypothesis and form hypothesis. 
        2.	How does resale price vary throughout Singapore, with respect to other relevant factors such as flat type, floor area, number of levels etc.?
        3.	Can these information help in choosing a resale flat? 
        4. [Geospatial](pages/1_🏠_EDA.py) visuals of 2015 transactions 

        **Datasets**
        - Original Dataset: [HDB Resale Flat Prices](https://data.gov.sg/dataset/resale-flat-prices)
        - Cleaned Dataset: [1990-2020 Dataset](artifacts/hdb_resale.parquet)
        - 2015 Transactions with Coordinates Dataset: [2015 Geocoded Resale Transactions](artifacts/2015_geocoded.parquet)
        """
    )

    with st.expander("References - Click to expand "):
        st.markdown(
            """
            1. Kaggle Dataset: [Singapore HDB Flat Resale Prices (1990-2020)](https://www.kaggle.com/datasets/teyang/singapore-hdb-flat-resale-prices-19902020)
            2. Medium Article: [Data-Driven Approach to Understanding HDB Resale Prices in Singapore](https://towardsdatascience.com/data-driven-approach-to-understanding-hdb-resale-prices-in-singapore-31c3beecfd97)
            """
        )


if __name__ == "__main__":
    main()