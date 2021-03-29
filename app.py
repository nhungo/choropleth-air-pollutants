import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
import dash  # pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)
server = app.server

dtype_dic= {'county_fips_code': str,
            'state_fips_code' : str}
df = pd.read_csv("sample_data_forecast.csv", dtype=dtype_dic)

data = df.groupby(['county_fips_code','county_name','state'])[['aqi']].mean().reset_index()
print(round(data['aqi'].max()))

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

fig = px.choropleth(data, geojson=counties, locations='county_fips_code', color='aqi',
                        color_continuous_scale="matter",
                        scope="usa",
                        range_color= (0,round(data['aqi'].max())),
                        hover_data=['county_name','state', 'aqi'],
                        labels={'aqi': 'AQI'}
                        )
fig.update_layout(height = 650,
                  margin ={"r":0,"t":0,"l":0,"b":0})

counties_list = data['county_name'].unique()
# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("A Recommendation System for New Homeowners based on AQI ", style={'text-align': 'center'}),
    dcc.Graph(id='choropleth', figure=fig),

    html.Br(),
    html.Br(),
    html.Div(["Select County:",
              dcc.Dropdown(id="county-select",
                           options = [{'label':i, 'value': i} for i in counties_list],
                           value='Autauga')
    ],
             style={'width': '30%',
                    'margin-left': 100,
                    'display': 'inline-block','float': 'none','text-align':'left'})


])




# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
