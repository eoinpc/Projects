import streamlit as st
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

# import emoji <------ GET THIS PACKAGE SOMEHOW

from st_aggrid import JsCode
from st_aggrid import AgGrid, GridOptionsBuilder

# Reading in data
df = pd.read_csv('messages_cleaned.csv')
df.drop(['Unnamed: 0'], axis = 1, inplace = True)
df

# df_text is data only containing text in messages (no links, embeds, images, etc.) - useful for text analysis/prediction
df_text = df[df['contains_media'] == False]

# 

