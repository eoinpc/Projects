import pandas as pd
import numpy as np
import datetime
import emoji
import string
import dash
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc, Input, Output, State, callback

dash.register_page(__name__, path = '/')

layout = [
    html.Div([html.P(children = 'This dashboard focuses on data spanning almost 3 years in a group chat with some of my friends. All in all, there are a combined 114,728 messages from 15 people.')]),
    html.Div([html.P(children = '\n')]),
]
