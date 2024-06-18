import pandas as pd
import numpy as np
import base64
import datetime
import emoji
import string
import dash
import nltk
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import dash_bootstrap_components as dbc
from wordcloud import WordCloud
from nltk.corpus import stopwords
from dash import Dash, html, dcc, Input, Output, State, callback
from plotly.subplots import make_subplots
from pyvis.network import Network
from io import BytesIO

df = pd.read_csv('messages_cleaned.csv')
df.drop('Unnamed: 0', axis = 1, inplace = True)
df_sample = df[['Author', 'Date', 'Content']]
df_sample = df_sample.sample(10)

df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Day'] = df['Date'].dt.day
df['Hour'] = df['Date'].dt.hour

month_mapping = {1: 'January', 
                 2: 'February', 
                 3: 'March', 
                 4: 'April',
                 5: 'May', 
                 6: 'June', 
                 7: 'July', 
                 8: 'August',
                 9: 'September', 
                 10: 'October', 
                 11: 'November', 
                 12: 'December'
}

df['Month'] = df['Month'].map(month_mapping)

app = Dash(__name__, external_stylesheets = [dbc.themes.FLATLY], use_pages = True)

app.layout = html.Div([
    html.H1('Welcome to the Dashboard!'),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']}", href = page['relative_path'])
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
])

if __name__ == "__main__":
    app.run_server(debug=True)
