import numpy as np
import pandas as pd



def wrangle_eod_chain_data(df,date_to_compute_DTE, source, put_call = False):

    """
    Example:
    df_ready_calls_puts = wrangle_eod_chain_data(df, datetime(2023, 10, 12, 10, 23))
    sources: yahoofinance or thetadata
    """
    if source == "yahoofinance":
        df = df.copy()
        df = df.rename(columns={'optionType': 'Right', 'expiration': 'Expiration', "strike": "Strike", "lastPrice" : "Close",
                                "bid": "Bid", "ask": "Ask", "openInterest": "OI", "volume": "Volume", "impliedVolatility": "OI",
                                "contractSymbol": "Contract_id"
                                })
        #df['Expiration'] = pd.to_datetime(df['Expiration'], format='%Y%m%d')
        df["Expiration"] =  pd.to_datetime(df['Expiration']) + pd.to_timedelta('11:59:00')
        
        #df =df.sort_values(by = "Expiration")
        df['Strike'] = df['Strike'].astype(float)
        df['DTE'] = (df['Expiration'] - date_to_compute_DTE).dt.days / 365
        df['Maturity_days'] = (df['Expiration'] - date_to_compute_DTE).dt.days

        df["mid"] = (df["Bid"] + df["Ask"])/2
        if put_call:
            df = df[df["Right"] == put_call] 
    
    if source =="thetadata":
        df = df.copy()
        df =df.sort_values(by = "Expiration")
        
        df['Date'] = pd.to_datetime(df['Date'], format='%Y%m%d')
        df['Expiration'] = pd.to_datetime(df['Expiration'], format='%Y%m%d')
        df["Expiration"] =  pd.to_datetime(df['Expiration']) + pd.to_timedelta('11:59:00')

        df['Strike'] = df['Strike'].astype(str).str[:3] + '.' + df['Strike'].astype(str).str[3:]
        df['Strike'] = df['Strike'].astype(float)
        df['DTE'] = (df['Expiration'] - date_to_compute_DTE).dt.days / 365
        df['Maturity_days'] = (df['Expiration'] - date_to_compute_DTE).dt.days
        #df = df[df["Volume"] > 2]
        df = df.rename(columns={'Close Price': 'Close'})

        if put_call:
            df = df[df["Right"] == put_call] 

    return df.reset_index(drop=True)


import plotly.graph_objs as go

def plot_3D(df, unique_parameter, z_column):
    """
    Unique parameter: Some parameter based on which you can create the y-axis, e.g., Maturity days or expiration
    Z_column: Column to plot, e.g., IV, prices
    """

    fig = go.Figure(data=[go.Mesh3d(
        x=df[unique_parameter],
        y=df['Strike'],
        z=df[z_column],
        color='mediumblue',
        opacity=0.75,
        colorscale='Viridis'
    )])
    
    marker_color = 'red'

    fig.add_scatter3d(
        x=df[unique_parameter],
        y=df['Strike'],
        z=df[z_column], 
        mode='markers',    
        marker=dict(
            color=marker_color
        ),
        opacity=0.9
    )

    fig.update_layout(
        title_text='Market Prices',
        scene=dict(
            xaxis_title=f'{unique_parameter}',
            yaxis_title='S (Strike)',
            zaxis_title=f'{z_column} ',
            bgcolor='white'  # Set the background color here
        ),
        height=600,
        width=1000
    )
    fig.update_layout(template="plotly+ggplot2")

    fig.show()