import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from urllib.request import urlopen
import json
import dash  
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)
server = app.server

dtype_dic= {'fips_code': str,
            'state_fips': str}
df = pd.read_csv("data/choropleth_data.csv", dtype=dtype_dic)

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

fig = px.choropleth(df, geojson=counties, locations='fips_code', color='avg_aqi',
                        color_continuous_scale="matter",
                        scope="usa",
                        range_color= (0,round(df['avg_aqi'].max())),
                        hover_data=['county_name','state_name', 'avg_aqi'],
                        labels={'avg_aqi': 'AQI','state_name':'State',}
                        )
fig.update_layout(height = 650,
                  margin ={"r":0,"t":0,"l":0,"b":0})

# App layout
app.layout = html.Div([
    html.H1("Hazardous Air Pollutants",style={'text-align': 'center'}),
    html.H2("A Recommendation System for New Homeowners based on Air Quality Index (AQI) Level", style={'text-align': 'center'}) ,
    dcc.Graph(id='choropleth', figure=fig),

    html.Br()


])




if __name__ == '__main__':
    app.run_server(debug=True)
