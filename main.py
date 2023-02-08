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


        [Dataset: HDB Resale Flat Prices](https://data.gov.sg/dataset/resale-flat-prices)
        """
    )


if __name__ == "__main__":
    main()