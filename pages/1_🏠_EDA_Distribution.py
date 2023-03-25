# Script for first page of Streamlit on EDA
import pandas as pd
import yaml
import streamlit as st
import plotly.express as px
from src.utility import load_parquet, slice_features, slice_year_range

with open("config.yml", encoding="utf-8", mode='r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.Loader)
    artifacts_path = cfg['eda']['artifacts_path']

def plot_transacts(df,col:str):
    """
    Plots a bar chart of the number of transactions for each type of flat.

    Args:
        df (pandas.DataFrame): A pandas DataFrame containing the data to be plotted. 
            Must have a 'flat_type' column.
        
        col (string): a valid string that must match column values of the input dataframe

    Returns:
        plotly.graph_objs._figure.Figure: A plotly bar chart figure object.
    """
    if col in df.columns:
        # Create a DataFrame grouped by col variable and count the number of transactions for each variable
        df_transacts = pd.DataFrame(df.groupby([col])[col].count())
        # Rename the column to 'num_transactions'
        df_transacts.columns = ['num_transactions']
        # Sort the DataFrame by number of transactions in descending order
        df_transacts = df_transacts.sort_values(by=['num_transactions'], ascending=False).reset_index()

        # Create a bar chart using Plotly Express
        fig = px.bar(
            df_transacts, 
            x=col, 
            y='num_transactions', 
            text_auto=True, 
            title=f"Number of Transactions in each {col.replace('_',' ').title()}"
            ).update_layout(
            xaxis_title=col.replace('_',' ').title(),
            yaxis_title = f"Number of Transactions"
            )
        

        return fig
        
    else:
        # If 'town' column is not present in DataFrame, print an error message
        st.write(f"{col} attribute is not present in the data set")

def main():
    """
    First page of Streamlit app to render EDA visualisations
    """

    st.set_page_config(
        page_title="Second page of streamlit app",
        page_icon='🏠',
        layout="wide",
    )

    st.title("Exploratory Data Analysis of HDB Resale Transactions")

    # load data artifact
    df_load = load_parquet(f'{artifacts_path}/hdb_resale.parquet')

    # SIDEBAR
    with st.sidebar:

        # SELECT_SLIDER - YEAR RANGE
        date_range_lst = df_load.year.unique()
        date_range_lst.sort()

        start_year, end_year = st.select_slider(
            "Select range of years",
            options=date_range_lst,
            value=(date_range_lst[-11],date_range_lst.max())
        )
        st.write('You selected year range between', start_year, 'and', end_year)

        # MULTISELECT - FLAT TYPE
        flat_type_fields = df_load['flat_type'].unique()
        sel_flat_type = st.multiselect(
            "Select flat types",
            options=flat_type_fields
                )

        # MULTISELECT - TOWN
        town_fields = df_load['town'].unique()
        sel_town = st.multiselect(
                    "Select town",
                    options=town_fields
                )
        
        # MULTISELECT - FLAT MODEL
        flat_model_fields = df_load['flat_model'].unique()
        sel_flat_model = st.multiselect(
                    "Select flat model",
                    options=flat_model_fields
                )
        
        st.write("This dashboard is created by [Leon Sun](https://github.com/leonswl). The source code for this project is published in this [GitHub Repository](https://github.com/leonswl/hdb-resale).")

    # END - SIDEBAR
    
    # slice year range based on user's selected range
    df_resale = slice_year_range(df_load, start_year=start_year, end_year=end_year)

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
        df_resale = df_resale.copy()

    # Otherwise, apply the specified filters to the input DataFrame using the slice_features function.
    else:
        df_resale = slice_features(
                        df_resale, 
                        sel_flat_type=sel_flat_type, 
                        sel_town=sel_town, 
                        sel_flat_model=sel_flat_model)
        
    # METRICS
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions",len(df_resale))
    col2.metric("Highest Transaction", f"S${int(max(df_resale['resale_price']))}")
    top_town = pd.DataFrame(df_resale.groupby(['town'])['town'].count()).rename(columns={'town':'count'}).sort_values(by=['count'],ascending=False).iloc[0].name
    col3.metric("Most Popular Town",top_town.title())

    st.write()

    # END - METRICS

    # DATAFRAME SNIPPET
    with st.expander("Expand to see snippet of dataframe"):
        st.dataframe(df_resale[:10000])

    tab1, tab2 = st.tabs(["Features", "Resale Price"])

    with tab1:
        st.markdown(
            """
            ## Features Distribution
            """
        )
        # DISTRIBUTION BAR PLOTS
        st.markdown(
            """
            ## Distribution
            """
        )
        # plots for town, flat_type, storey_range and month
        for col in ['town','flat_type','storey_range', 'flat_model','month']:
            fig_transacts = plot_transacts(df_resale,col)  
            st.plotly_chart(fig_transacts, use_container_width=True)      

    with tab2:
        st.markdown(
            """
            ## Resale Price Distribution
            """
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            # SLIDER - BIN WIDTH
            bin_width = st.slider(
                "Select bin width",
                min_value=10,
                max_value=1000,
                step=10,
                value=500
            )
            st.write('You select a bin width of', bin_width, 'for the resale price distribution plot')

        with col2:
            # RADIO - DISTRIBUTION
            dist_type = st.radio(
                "Select distribution type",
                options=('box','violin')
            )
            st.markdown(f"You selected `{dist_type}` distribution")

        with col3:
            # RADIO - SPLIT FEATURES
            add_field = st.radio(
                "Split further with:",
                options=("None","flat_type","town","storey_range",'flat_model')
            )
            

        with col4:
            if add_field != 'None':
                field_options = st.multiselect(
                    "Choose a maximum of 4 options to be included in the distribution plot",
                    options=df_resale[add_field].unique(),
                    max_selections=4
                )

        if add_field == 'None':
            # plot for resale price
            fig_price = px.histogram(
                df_resale.sort_values(by='year'),
                x="resale_price",
                nbins=bin_width,
                title='Distribution of Transactions for Resale Price',
                marginal=dist_type,
                animation_frame="year",
                range_x=[df_resale.resale_price.min(), df_resale.resale_price.max()],
                barmode="overlay",
            ).update_layout(
                xaxis_title="Resale Price (S$)",
                yaxis_title="Frequency",
            )
            st.plotly_chart(fig_price, use_container_width=True)

        else:

            df_resale_price = df_resale.loc[df_resale[add_field].isin(field_options)]
            # plot for resale price
            fig_price = px.histogram(
                df_resale_price.sort_values(by='year'),
                x="resale_price",
                nbins=bin_width, 
                title='Distribution of Transactions for Resale Price',
                color=add_field,
                marginal=dist_type,
                animation_frame="year",
                range_x=[df_resale_price.resale_price.min(), df_resale_price.resale_price.max()],
                barmode="overlay",
            ).update_layout(
                xaxis_title="Resale Price (S$)",
                yaxis_title="Frequency",
            )
            st.plotly_chart(fig_price, use_container_width=True)

if __name__ == "__main__":
    main()
