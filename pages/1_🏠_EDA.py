# Script for first page of Streamlit on EDA
import pandas as pd
import yaml
import streamlit as st
import plotly.express as px

with open("config.yml", encoding="utf-8", mode='r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.Loader)
    artifacts_path = cfg['eda']['artifacts_path']

# cache data to avoid reloading data
@st.cache(ttl=300)
def load_parquet(path_filename):
    df_loaded = pd.read_parquet(path_filename)
    return df_loaded

def main():
    """
    First page of Streamlit app to render EDA visualisations
    """

    st.set_page_config(
        page_title="Second page of streamlit app",
        page_icon='🏠'
    )

    st.title("Exploratory Data Analysis of HDB Resale Transactions")

    st.write("""
    I’ll perform initial investigations of the dataset to discover any patterns and anomalies, and also check hypothesis and form hypothesis. 
    """)

    df_resale = load_parquet(f'{artifacts_path}/hdb_resale.parquet')

    with st.expander("Expand to see snippet of dataframe"):
        st.dataframe(df_resale[:10000])

    df_town = pd.DataFrame(df_resale.groupby(['town']).town.count())
    df_town.columns = ['num_transactions']
    df_town = df_town.reset_index()


    fig_town = px.bar(df_town, x='town', y='num_transactions',text_auto=True, title="Number of Transactions in each Town")

    st.plotly_chart(fig_town, use_container_width=True)

    df_flat_type = pd.DataFrame(df_resale.groupby(['flat_type']).flat_type.count())
    df_flat_type.columns = ['num_transactions']
    df_flat_type = df_flat_type.reset_index()

    fig_flat_type = px.bar(df_flat_type, x='flat_type', y='num_transactions',text_auto=True, title="Number of Transactions for each type of flat")

    st.plotly_chart(fig_flat_type, use_container_width=True)


if __name__ == "__main__":
    main()
