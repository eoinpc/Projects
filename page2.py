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
from dash.dependencies import Input, Output
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

dash.register_page(__name__)

layout = [
    html.Div([
        html.P('\n \n'),
        html.P('Select a feature to explore:'),

        dcc.Dropdown(
            id = 'feature-dd',
            options = [
                {'label': 'Message Length', 'value': 'len'},
                {'label': 'Message Count', 'value': 'count'},
                {'label': 'Keywords', 'value': 'keyword'},
                {'label': 'Phrases', 'value': 'phrase'}
            ],
            value = 'len',
            placeholder = 'Select a feature to explore.'
        ),

        html.P('\n'),
        html.P('Select a timeframe:'),

        dcc.Dropdown(
            id = 'timeframe-dd',
            value = ['year', None],
            multi = True
        ),

        html.P('\n'),

        dcc.Graph(id = 'graph')
    ])
]

@callback(
    Output(component_id = 'timeframe-dd', component_property = 'options'),
    [Input(component_id = 'feature-dd', component_property = 'value')]
)

def timeframe_options(feature):
    if feature == 'len' or feature == 'count':
        return [{'label': 'Yearly', 'value': 'year'},
                {'label': 'Monthly', 'value': 'month'},
                {'label': 'Daily', 'value': 'day'},
                {'label': 'Hourly', 'value': 'hour'}]
    
    elif feature == 'keyword' or feature == 'phrase':
        return [{'label': 'All Time', 'value': 'all'},
                {'label': 'Yearly', 'value': 'year'},
                {'label': 'Hourly', 'value': 'hour'}]

@callback(
    Output(component_id = 'graph', component_property = 'figure'),
    [Input(component_id = 'feature-dd', component_property = 'value'),
     Input(component_id = 'timeframe-dd', component_property = 'value')]
)

def update_graph(feature, timeframe):
    # filtering out links/images so that message length is not skewed by these longer messages with no meaning
    df_text = df[df['contains_media'] == False]

    # Message length feature
    if feature == 'len':
        df_text['msg_len'] = df['Content'].str.len()

        if len(timeframe) == 1:
            timeframe1 = timeframe[0]
            timeframe2 = None

        elif len(timeframe) > 1:
            timeframe1, timeframe2 = timeframe

        if (timeframe1 == 'year' and timeframe2 == 'month') or (timeframe2 == 'year' and timeframe1 == 'month'):
            months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

            avg_len_by_monthyear = df_text.groupby(['Year', 'Month']).agg(avg_len = ('msg_len', 'mean')).reset_index()

            frames = []
            for month in months:
                var_value = avg_len_by_monthyear[avg_len_by_monthyear['Month'] == month]
                frames.append(var_value)

            fig = go.Figure()

            for i, frame in enumerate(frames):
                fig.add_trace(go.Scatter(x = frame['Year'], y = frame['avg_len'], mode = 'lines', name = f'{i}'))        

            fig.update_layout(
                xaxis = dict(title = 'Year'),
                yaxis = dict(title = 'Average Message Length (characters)')
            )
            
            return fig
        
        elif (timeframe1 == 'year' and timeframe2 == 'day') or (timeframe2 == 'year' and timeframe1 == 'day'):
            avg_len_by_yearday = df_text.groupby(['Year', 'Day']).agg(avg_len = ('msg_len', 'mean')).reset_index()

            fig = make_subplots(
                rows = 1, 
                cols = 4, 
                subplot_titles = ('Message Length 2021', 'Message Length 2022', 'Message Length 2023', 'Message Length 2024'),
                specs = [[{'type': 'polar'}, {'type': 'polar'}, {'type': 'polar'}, {'type': 'polar'}]]
            )
            
            frames = []
            for year in [2021, 2022, 2023, 2024]:
                var_value = avg_len_by_yearday[avg_len_by_yearday['Year'] == year]
                frames.append(var_value)

            theta = avg_len_by_yearday['Day'].unique()
            theta = [value.astype(str) for value in theta]

            for i, frame in enumerate(frames):
                fig.add_trace(go.Barpolar(r = frame['avg_len'], theta = theta), row = 1, col = i + 1)

            days = list(avg_len_by_yearday['Day'].unique())

            fig.update_layout(
                polar = dict(
                    radialaxis = dict(showticklabels = True, ticks = ''),
                    angularaxis = dict(
                        tickmode = 'array',
                        tickvals = days,
                        ticktext = [str(day) for day in days]
                    )
                ),
                showlegend = False
            )

            fig.update_polars(angularaxis_direction = 'clockwise')
            fig.update_layout(showlegend = False)

            return fig
        
        elif (timeframe1 == 'year' and timeframe2 == 'hour') or (timeframe2 == 'year' and timeframe1 == 'hour'):
            avg_len_by_yearhour = df_text.groupby(['Year', 'Hour']).agg(avg_len = ('msg_len', 'mean')).reset_index()

            fig = make_subplots(
                rows = 1, 
                cols = 4, 
                subplot_titles = ('Message Length 2021', 'Message Length 2022', 'Message Length 2023', 'Message Length 2024'),
                specs = [[{'type': 'polar'}, {'type': 'polar'}, {'type': 'polar'}, {'type': 'polar'}]])
            
            frames = []
            for year in [2021, 2022, 2023, 2024]:
                var_value = avg_len_by_yearhour[avg_len_by_yearhour['Year'] == year]
                frames.append(var_value)

            theta = avg_len_by_yearhour['Hour'].unique()
            theta = [value.astype(str) for value in theta]

            for i, frame in enumerate(frames):
                fig.add_trace(go.Barpolar(r = frame['avg_len'], theta = theta), row = 1, col = i + 1)

            hours = list(avg_len_by_yearhour['Hour'].unique())

            fig.update_layout(
                polar = dict(
                    radialaxis = dict(showticklabels = True, ticks = ''),
                    angularaxis = dict(
                        tickmode = 'array',
                        tickvals = hours,
                        ticktext = [str(hour) for hour in hours]
                    )
                ),
                showlegend = False
            )

            fig.update_polars(angularaxis_direction = 'clockwise')
            fig.update_layout(showlegend = False)

            return fig
        
        elif (timeframe1 == 'month' and timeframe2 == 'day') or (timeframe2 == 'month' and timeframe1 == 'day'):
            avg_len_by_monthday = df_text.groupby(['Month', 'Day']).agg(avg_len = ('msg_len', 'mean')).reset_index()
            months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

            fig = make_subplots(
                rows = 3, 
                cols = 4, 
                subplot_titles = ('January Message Length', 'February Message Length', 'March Message Length', 'April Message Length', 'May Message Length', 'June Message Length', 
                                  'July Message Length', 'August Message Length', 'September Message Length', 'October Message Length', 'November Message Length', 'December Message Length'),
                specs = [[{'type': 'polar'}, {'type': 'polar'}, {'type': 'polar'}, {'type': 'polar'}], [{'type': 'polar'}, {'type': 'polar'}, 
                          {'type': 'polar'}, {'type': 'polar'}], [{'type': 'polar'}, {'type': 'polar'}, {'type': 'polar'}, {'type': 'polar'}]])
            
            frames = []
            for month in months:
                var_value = avg_len_by_monthday[avg_len_by_monthday['Month'] == month]
                frames.append(var_value)

            theta = avg_len_by_monthday['Day'].unique()
            theta = [value.astype(str) for value in theta]

            for i, frame in enumerate(frames):
                fig.add_trace(go.Barpolar(r = frame['avg_len'], theta = theta), row = i // 4 + 1, col = i % 4 + 1)

            days = list(avg_len_by_monthday['Day'].unique())

            fig.update_layout(
                polar = dict(
                    radialaxis = dict(showticklabels = True, ticks = ''),
                    angularaxis = dict(
                        tickmode = 'array',
                        tickvals = days,
                        ticktext = [str(day) for day in days]
                    )
                ),
                showlegend = False
            )

            fig.update_polars(angularaxis_direction = 'clockwise')
            fig.update_layout(showlegend = False)

            return fig

        elif timeframe1 == 'year':
            len_by_year = df_text.groupby('Year').agg(avg_len = ('msg_len', 'mean')).reset_index()

            fig = px.line(len_by_year, len_by_year['Year'], len_by_year['avg_len'])
            fig.update_layout(
                xaxis = dict(title = 'Year'),
                yaxis = dict(title = 'Average Message Length (characters)')
            )

            return fig

        elif timeframe1 == 'month':
            len_by_month = df_text.groupby('Month').agg(avg_len = ('msg_len', 'mean')).reset_index()

            fig = px.line(len_by_month, len_by_month['Month'], len_by_month['avg_len'])
            fig.update_layout(
                xaxis = dict(title = 'Month'),
                yaxis = dict(title = 'Average Message Length (characters)')
            )

            return fig

        elif timeframe1 == 'day':
            len_by_day = df_text.groupby('Day').agg(avg_len = ('msg_len', 'mean')).reset_index()

            fig = px.line(len_by_day, len_by_day['Day'], len_by_day['avg_len'])
            fig.update_layout(
                xaxis = dict(title = 'Day'),
                yaxis = dict(title = 'Average Message Length (characters)')
            )

            return fig
        
        elif timeframe1 == 'hour':
            len_by_hour = df_text.groupby('Hour').agg(avg_len = ('msg_len', 'mean')).reset_index()

            fig = px.line(len_by_hour, len_by_hour['Hour'],len_by_hour['avg_len'])
            fig.update_layout(
                xaxis = dict(title = 'Hour'),
                yaxis = dict(title = 'Average Message Length (characters)')
            )

            return fig
        
        


    # Message count feature
    if feature == 'count':
        if timeframe == 'year':
            msgs_by_year = df_text.groupby('Year').agg(msg_count = ('Content', 'count')).reset_index()

            fig = px.bar(msgs_by_year, msgs_by_year['Year'], msgs_by_year['msg_count'])
            fig.update_layout(
                xaxis = dict(title = 'Year'),
                yaxis = dict(title = 'Number of Messages')
            )

            return fig

        elif timeframe == 'month':
            msgs_by_month = df_text.groupby('Month').agg(msg_count = ('Content', 'count')).reset_index()

            fig = px.bar(msgs_by_month, msgs_by_month['Month'], msgs_by_month['msg_count'])
            fig.update_layout(
                xaxis = dict(title = 'Month'),
                yaxis = dict(title = 'Number of Messages')
            )

            return fig

        elif timeframe == 'day':
            msgs_by_day = df_text.groupby('Day').agg(msg_count = ('Content', 'count')).reset_index()
            theta = msgs_by_day['Day'].unique()
            theta = [value.astype(str) for value in theta]

            fig = go.Figure()
            fig.add_trace(go.Barpolar(r = msgs_by_day['msg_count'], theta = theta))

            days = list(msgs_by_day['Day'].unique())

            fig.update_layout(
                polar = dict(
                    radialaxis = dict(showticklabels = True, ticks = ''),
                    angularaxis = dict(
                        tickmode = 'array',
                        tickvals = days,
                        ticktext = [str(day) for day in days]
                    )
                ),
                showlegend = False
            )

            fig.update_polars(angularaxis_direction = 'clockwise')
            fig.update_layout(showlegend = False)

            return fig

        elif timeframe == 'hour':
            msgs_by_hour = df_text.groupby('Hour').agg(msg_count = ('Content', 'count')).reset_index()
            theta = msgs_by_hour['Hour'].unique()
            theta = [value.astype(str) for value in theta]

            fig = go.Figure()
            fig.add_trace(go.Barpolar(r = msgs_by_hour['msg_count'], theta = theta))

            hours = list(msgs_by_hour['Hour'].unique())

            fig.update_layout(
                polar = dict(
                    radialaxis = dict(showticklabels = True, ticks = ''),
                    angularaxis = dict(
                        tickmode = 'array',
                        tickvals = hours,
                        ticktext = [str(hour) for hour in hours]
                    )
                ),
                showlegend = False
            )

            fig.update_polars(angularaxis_direction = 'clockwise')
            fig.update_layout(showlegend = False)

            return fig

    # Keyword feature
    if feature == 'keyword':
        if timeframe == 'all':
            stopwords_list = stopwords.words('english')
            additional_stopwords = ['walid', 'sakun', 'mika', 'tosin', 'chris', 'vishal', 'devin', 'michael', 'alex', 'chri', 'eoin', 'im', 'u']
            stopwords_list += additional_stopwords
            text = ' '.join(df_text['Content'])

            translator = str.maketrans('', '', string.punctuation)
            text = text.translate(translator).lower()

            words = nltk.word_tokenize(text)
            words = [t for t in words if t not in stopwords_list]
            text = ' '.join(words)

            wc = WordCloud().generate(text)
            plt.axis('off')

            img_data = BytesIO()
            wc.to_image().save(img_data, format = 'PNG')
            img_data.seek(0)
            img_base64 = base64.b64encode(img_data.read()).decode('utf-8')

            fig = go.Figure()
            fig.add_layout_image(
                source = f"data:image/png;base64,{img_base64}",
                x = 0,
                y = 1,
                xref = 'paper',
                yref = 'paper',
                sizex = 1,
                sizey = 1,
                opacity = 1,
                layer = 'above'
            )

            fig.update_layout(
                xaxis = dict(visible = False),
                yaxis = dict(visible = False),
                plot_bgcolor = 'rgba(0, 0, 0, 0)'
            )

            return fig

        elif timeframe == 'year':
            fig = make_subplots(rows = 1, cols = 4, subplot_titles = ('Keywords 2021', 'Keywords 2022', 'Keywords 2023', 'Keywords 2024'))

            sources = []

            for i, year in enumerate(df_text['Year'].unique()):
                df_filtered = df_text[df_text['Year'] == year]
                stopwords_list = stopwords.words('english')
                additional_stopwords = ['walid', 'sakun', 'mika', 'tosin', 'chris', 'vishal', 'devin', 'michael', 'alex', 'chri', 'eoin', 'im', 'u']
                stopwords_list += additional_stopwords
                text = ' '.join(df_filtered['Content'])

                translator = str.maketrans('', '', string.punctuation)
                text = text.translate(translator).lower()

                words = nltk.word_tokenize(text)
                words = [t for t in words if t not in stopwords_list]
                text = ' '.join(words)

                wc = WordCloud().generate(text)
                plt.axis('off')

                img_data = BytesIO()
                wc.to_image().save(img_data, format = 'PNG')
                img_data.seek(0)

                var_value =  base64.b64encode(img_data.read()).decode('utf-8')
                sources.append(var_value)
            
            for i, source in enumerate(sources):
                fig.add_layout_image(
                    source = f"data:image/png;base64,{source}",
                    x = 0,
                    y = 4,
                    xref = 'paper',
                    yref = 'paper',
                    sizex = 6,
                    sizey = 8,
                    opacity = 1,
                    layer = 'above',
                    row = 1,
                    col = i + 1
                )

                fig.update_layout({
                    f'xaxis{i + 1}': {'visible': False},
                    f'yaxis{i + 1}': {'visible': False}
                })
                
            return fig
        
 # NOT APPLICABLE FOR KEYWORDS
        elif timeframe == 'month':
            len_by_month = df_text.groupby('Month').agg(avg_len = ('msg_len', 'mean')).reset_index()
            x = len_by_month['Month']
            y = len_by_month['avg_len']

        elif timeframe == 'day':
            len_by_day = df_text.groupby('Day').agg(avg_len = ('msg_len', 'mean')).reset_index()
            x = len_by_day['Day']
            y = len_by_day['avg_len']

        elif timeframe == 'hour':
            len_by_hour = df_text.groupby('Hour').agg(avg_len = ('msg_len', 'mean')).reset_index()
            x = len_by_hour['Hour']
            y = len_by_hour['avg_len']

    # Engagement feature -- needs some work
    '''
    if feature == 'engagement':
        df_text['msg_len'] = df['Content'].str.len()
        if timeframe == 'all':
            x = 'All'
            y = df_text['msg_len'].mean()

        elif timeframe == 'year':
            len_by_year = df_text.groupby('Year').agg(avg_len = ('msg_len', 'mean')).reset_index()
            x = len_by_year['Year']
            y = len_by_year['avg_len']

        elif timeframe == 'month':
            len_by_month = df_text.groupby('Month').agg(avg_len = ('msg_len', 'mean')).reset_index()
            x = len_by_month['Month']
            y = len_by_month['avg_len']

        elif timeframe == 'day':
            len_by_day = df_text.groupby('Day').agg(avg_len = ('msg_len', 'mean')).reset_index()
            x = len_by_day['Day']
            y = len_by_day['avg_len']

        elif timeframe == 'hour':
            len_by_hour = df_text.groupby('Hour').agg(avg_len = ('msg_len', 'mean')).reset_index()
            x = len_by_hour['Hour']
            y = len_by_hour['avg_len']
'''
