# Script for first page of Streamlit on EDA
import pandas as pd
import yaml
import streamlit as st
import plotly.express as px

with open("config.yml", encoding="utf-8", mode='r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.Loader)
    artifacts_path = cfg['eda']['artifacts_path']

# cache data to avoid reloading data
@st.cache_data(ttl=300)
def load_parquet(path_filename):
    """
    Loads a Parquet file located at the given path and filename into a pandas DataFrame.

    Args:
    - path_filename: string containing the path and filename of the Parquet file to be loaded

    Returns:
    - pandas DataFrame containing the contents of the Parquet file
    """
    
    # Use pandas' read_parquet() function to load the Parquet file into a DataFrame
    
    return pd.read_parquet(path_filename)

def slice_year_range (df, start_year, end_year):
    """
    Filters a pandas DataFrame to include only rows where the value of 'year' column is greater than 
    the 'start_year' variable and less than the 'end_year' variable.

    Args:
    - df: pandas DataFrame with a column named 'year'

    Returns:
    - pandas DataFrame with only rows where the 'year' value is greater than 'start_year' and less than 'end_year'
    """
    
    # Filter the DataFrame to only include rows where the 'year' value is greater than 'start_year'
    # and less than 'end_year'
    return df.loc[(df['year']>start_year) & (df['year']<end_year)]


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
        fig = px.bar(df_transacts, x=col, y='num_transactions', text_auto=True, title=f"Number of Transactions in each {col.replace('_',' ').title()}")

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
            value=(date_range_lst.min(),date_range_lst.max())
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
    # END - SIDEBAR

    # METRICS
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Transactions",len(df_load))
    col2.metric("Highest Transaction", f"S${int(max(df_load['resale_price']))}")
    col3.metric("Most Popular Town","Tampines")
    # END - METRICS

    
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
                st.markdown(f"You selected: `{field_options}`")

                st.write(type(field_options))

        if add_field == 'None':
            # plot for resale price
            fig_price = px.histogram(
                            df_resale,
                            x="resale_price",
                            nbins=bin_width, 
                            title='Distribution of Transactions for Resale Price',
                            marginal=dist_type)
            st.plotly_chart(fig_price, use_container_width=True)

        else:

            df_resale_price = df_resale.loc[df_resale[add_field].isin(field_options)]
            # plot for resale price
            fig_price = px.histogram(
                            df_resale_price,
                            x="resale_price",
                            nbins=bin_width, 
                            title='Distribution of Transactions for Resale Price',
                            color=add_field,
                            marginal=dist_type)
            st.plotly_chart(fig_price, use_container_width=True)

    


if __name__ == "__main__":
    main()
