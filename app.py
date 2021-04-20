import dash  # (version 1.12.0)
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from urllib.request import urlopen
import json

# Create an app
app = dash.Dash(__name__)
server = app.server

##### Loading and preparing data #####

# Choropleth data
dtype_dic= {'fips_code': str,
            'state_fips': str}
df_choro = pd.read_csv("choropleth_data.csv", dtype=dtype_dic)

# Supplementary visualizations data
df_supp = pd.read_csv("supplementary_viz.csv")

# Recommendations data
df_rec2022 = pd.read_csv("recommendations_2022.csv")

# Data from dropdown menu
df_fips_county = df_supp.groupby(['fips_code','county_name','state_name'],as_index = False).count()[["fips_code","county_name",'state_name']]
df_fips_county
data = {'label':list(df_fips_county["county_name"] + ", "+ df_fips_county["state_name"]),
        'value':list(df_fips_county["fips_code"])}
df_fips = pd.DataFrame(data)
df_fips = df_fips.to_dict('records')

# Obtaining geojson file
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)


##### Visualizations #####

# Choropleth figure
fig_choro = px.choropleth(df_choro, geojson=counties, locations='fips_code', color='avg_aqi',
                        color_continuous_scale="matter",
                        scope="usa",
                        range_color= (0,round(df_choro['avg_aqi'].max())),
                        hover_data = {'fips_code':False,
                                      'county_name':True,
                                      'state_name':True,
                                      'avg_aqi': ':.0f',
                                      'reliability':':.0%'},
                        labels={'avg_aqi': 'AQI','state_name':'state','county_name':'county'},
                        custom_data = ['county_name','state_name','reliability']
                        )
fig_choro.update_layout(height = 500, margin ={"r":0,"t":0,"l":0,"b":0})
fig_choro.update_traces(hovertemplate= "%{customdata[0]}, %{customdata[1]}<br>Average AQI: %{z:.2f} <br>Reliability Score: " + '%{customdata[2]:.0%}', selector=dict(type='choropleth'))


# App layout
app.layout = html.Div([
    # Title
    html.H1("Hazardous Air Pollutants",style={'text-align': 'center','font-family': 'arial'}),
    html.P("A Recommendation System for New Homeowners based on Air Quality Index (AQI) Level", 
            style={'text-align': 'center', 'font-family': 'courier new', 'margin-bottom':'50px', 'font-size':'16pt'}) ,
    html.Div(dcc.Graph(id='choropleth', figure=fig_choro), style = {'width': '60%','padding-left': '20%','padding-right':'20%'}),
    
    html.Br(),
    
    # Dropdown menu
    html.Div([
    
        html.Div(
            ["Select a county by clicking on the map above or from the dropdown menu: "] , 
            style={'font-family':'arial', "margin-top":"20px", 'display': 'inline-block', 
                      'padding-right': '15px'}
        ),

        html.Div(
            dcc.Dropdown(id='dropdown',
                         options = df_fips,
                         placeholder = "Please select or search for a county.",
                         clearable=False
                        ), 
        style={'width': '300px', 'display': 'inline-block', 'verticalAlign': 'middle', "text-align":"left"}
        ),
        
    ], style = {"text-align":"center"}),
    
    # Recommendations text box
    html.Div(id = "recommendation"),
    
    # Title for graphs
    html.H2(id = "current_location"),
    
    # Graphs (Historical and Forecast)
    html.Div(id = 'trend_graphs', 
             children = [ 
                 html.Div(
                    dcc.Graph(id='trend-co', figure = {}),
                    style={'display': 'inline-block', 'verticalAlign': 'middle'}
                ),
                html.Div(
                    dcc.Graph(id='trend-ozone', figure = {}),
                    style={'display': 'inline-block', 'verticalAlign': 'middle'}
                ),
                html.Div(
                    dcc.Graph(id='trend-no2', figure = {}),
                    style={'display': 'inline-block', 'verticalAlign': 'middle'}
                ),
                html.Div(
                    dcc.Graph(id='trend-so2', figure = {}),
                    style={'display': 'inline-block', 'verticalAlign': 'middle'}
                ),
                html.Div(
                    dcc.Graph(id='trend-pm', figure = {}),
                    style={'display': 'inline-block', 'verticalAlign': 'middle'}
                )
             ]
    ),
    
    # Educational Component Selection
    html.H1(children="What would you like to learn about?", 
             style={
                    "font-family":"arial", 
                    "padding-top":"30px",
                    "padding-bottom":"30px",
                    "padding-left":"20px",
                    "padding-right":"20px",
                    "width":"70%", 
                    "background-color":" rgb(205, 223, 247, 0.5)",
                    "border-radius": "10pt",
                    "color":"white",
                    "text-shadow": "2px 2px 4px #000000",
                    "text-align":"center",
                    "margin-top":"50px",
                    "margin-left":"auto",
                    "margin-right":"auto",
                   }),
    
    dcc.RadioItems(
        id='education',
        options=[
            {'label': 'AQI Values', 'value': 'AQI Values'},
            {'label': 'Carbon Monoxide', 'value': 'Carbon monoxide'},
            {'label': 'Ozone', 'value': 'Ozone'},
            {'label': 'Nitrogen Dioxide', 'value': 'Nitrogen dioxide (NO2)'},
            {'label': 'Sulfur Dioxide', 'value': 'Sulfur dioxide'},
            {'label': 'PM', 'value': 'PM2.5 - Local Conditions'}
        ],
        value='AQI Values',
        labelStyle={'display': 'inline-block','padding':'10px', "font-family": "arial", "font-size":"large",
                   "padding-bottom":"30px"},
        style = {'text-align':'center'}
    ),

    # Educational Component Information
    html.Div(id='educate_me')
    
    ])

# Callback for historical & forecast graphs
@app.callback(
    [Output(component_id='trend-co', component_property='figure'),
    Output(component_id='trend-ozone', component_property='figure'),
    Output(component_id='trend-no2', component_property='figure'),
    Output(component_id='trend-so2', component_property='figure'),
    Output(component_id='trend-pm', component_property='figure'),
    Output(component_id='recommendation', component_property='children'),
    Output(component_id='current_location', component_property='children')],
    [Input(component_id='choropleth', component_property='clickData'), 
     Input(component_id='dropdown', component_property='value')]
)  
def update_graph(choropleth_click_data, dropdown_data):

    # Starting condition
    if (choropleth_click_data is None) and (dropdown_data is None):
        county_fips = 1001
        county_name = 'Autauga County'
        state_name = 'Alabama'
        county_aqi = '20.85'
        
    else:
         
        # Find out if choropleth or dropdown was triggered
        triggered_id = dash.callback_context.triggered[0]['prop_id'].split('.')[0]

        if(triggered_id == 'choropleth'):
            county_fips = int(choropleth_click_data['points'][0]['location'])
            county_name = choropleth_click_data['points'][0]['customdata'][0]
            state_name = choropleth_click_data['points'][0]['customdata'][1]
            county_aqi = str(round(choropleth_click_data['points'][0]['z'],2))
            
        if(triggered_id == 'dropdown'):
            county_fips = dropdown_data
            county_name = df_choro.loc[pd.to_numeric(df_choro["fips_code"]) == county_fips,"county_name"].to_string(index = False)
            state_name = df_choro.loc[pd.to_numeric(df_choro["fips_code"]) == county_fips,"state_name"].to_string(index = False)
            county_aqi = round(df_choro.loc[pd.to_numeric(df_choro["fips_code"]) == county_fips,"avg_aqi"],2).to_string(index = False).strip()
    
    # Store selected county
    dff = df_supp[df_supp["fips_code"]==county_fips].copy()
    dff = dff[dff['date'] >= 2015]
    
    # Line chart for carbon monoxide
    fig_co = px.line(dff[dff["parameter_name"]=="Carbon monoxide"], x="date", y="avg_aqi", title='Historical Trend & Forecast for Carbon Monoxide', color="forecast", color_discrete_sequence=["red", "blue"])
    fig_co = fig_co.update_layout(height=450, width=500,title_x=0.5,legend_title_text="",legend_traceorder="reversed")
    fig_co = fig_co.update_traces(mode="markers+lines", 
                                  hovertemplate="Average AQI: %{y:.2f}"+"<br>Year: %{x}", 
                                  selector=dict(type='scatter'))
    fig_co = fig_co.update_xaxes(title_text="Year", tickvals=[2015,2016,2017,2018,2019,2020,2021,2022])
    fig_co = fig_co.update_yaxes(title_text="Average AQI")
    
    # Line chart for ozone
    fig_oz = px.line(dff[dff["parameter_name"]=="Ozone"], x="date", y="avg_aqi", 
                     title='Historical Trend & Forecast for Ozone',color="forecast",
                     color_discrete_sequence=["red", "blue"])
    fig_oz = fig_oz.update_layout(height=450, width=500,title_x=0.5,legend_title_text="",legend_traceorder="reversed")
    fig_oz = fig_oz.update_traces(mode="markers+lines", 
                                  hovertemplate="Average AQI: %{y:.2f}"+"<br>Year: %{x}", 
                                  selector=dict(type='scatter'))
    fig_oz = fig_oz.update_xaxes(title_text="Year", tickvals=[2015,2016,2017,2018,2019,2020,2021,2022])
    fig_oz = fig_oz.update_yaxes(title_text="Average AQI")
    
    # Line chart for Nitrogen Dioxide
    fig_no2 = px.line(dff[dff["parameter_name"]=="Nitrogen dioxide (NO2)"], x="date", y="avg_aqi", 
                     title='Historical Trend & Forecast for Nitrogen Dioxide',color="forecast",
                     color_discrete_sequence=["red", "blue"])
    fig_no2 = fig_no2.update_layout(height=450, width=500,title_x=0.5,legend_title_text="",legend_traceorder="reversed")
    fig_no2 = fig_no2.update_traces(mode="markers+lines", 
                                  hovertemplate="Average AQI: %{y:.2f}"+"<br>Year: %{x}", 
                                  selector=dict(type='scatter'))
    fig_no2 = fig_no2.update_xaxes(title_text="Year", tickvals=[2015,2016,2017,2018,2019,2020,2021,2022])
    fig_no2 = fig_no2.update_yaxes(title_text="Average AQI")
    
    # Line chart for Sulfur Dioxide
    fig_so2 = px.line(dff[dff["parameter_name"]=="Sulfur dioxide"], x="date", y="avg_aqi", 
                     title='Historical Trend & Forecast for Sulfur Dioxide',color="forecast",
                     color_discrete_sequence=["red", "blue"])
    fig_so2 = fig_so2.update_layout(height=450, width=500,title_x=0.5,legend_title_text="",legend_traceorder="reversed")
    fig_so2 = fig_so2.update_traces(mode="markers+lines", 
                                  hovertemplate="Average AQI: %{y:.2f}"+"<br>Year: %{x}", 
                                  selector=dict(type='scatter'))
    fig_so2 = fig_so2.update_xaxes(title_text="Year", tickvals=[2015,2016,2017,2018,2019,2020,2021,2022])
    fig_so2 = fig_so2.update_yaxes(title_text="Average AQI")
    
    # Line chart for PM2.5
    fig_pm = px.line(dff[dff["parameter_name"]=="PM2.5 - Local Conditions"], x="date", y="avg_aqi", 
                     title='Historical Trend & Forecast for PM2.5',color="forecast",
                     color_discrete_sequence=["red", "blue"])
    fig_pm = fig_pm.update_layout(height=450, width=500,title_x=0.5,legend_title_text="",legend_traceorder="reversed")
    fig_pm = fig_pm.update_traces(mode="markers+lines", 
                                  hovertemplate="Average AQI: %{y:.2f}"+"<br>Year: %{x}", 
                                  selector=dict(type='scatter'))
    fig_pm = fig_pm.update_xaxes(title_text="Year", tickvals=[2015,2016,2017,2018,2019,2020,2021,2022])
    fig_pm = fig_pm.update_yaxes(title_text="Average AQI")

    # Find recommended county based on selection
    rec_county2022 = df_rec2022.loc[df_rec2022["source_fips"]==county_fips,"rec_county_name"].to_string(index = False)
    rec_aqi2022 = df_rec2022.loc[df_rec2022["source_fips"]==county_fips,"rec_avg_aqi"]
    rec_aqi2022 = round(rec_aqi2022,2).to_string(index = False)

    # Return text for recommendation
    if rec_county2022 == county_name:
        recommendation_text = html.Div([
            html.H2("Recommendation"),
            "Based on your selected county, ",
            html.Strong(county_name),
            " in ",
            html.Strong(state_name),
            ", we recommend that you stick with your selection as it is forecasted to have the lowest average AQI among its neighbouring counties in 2022."
            ])
    else:
        recommendation_text = html.Div([
            html.H2("Recommendation"),
            "Based on your selected county, ",
            html.Strong(county_name),
            " in ",
            html.Strong(state_name),
            ", we recommend that you also consider its neighbouring county, ",
            html.Strong(rec_county2022),
            ", which is forecasted to have a lower average AQI of ",
            rec_aqi2022,
            " in 2022."
            ])
    
    current_location = "Historical Trends and Forecasts for " + county_name + ", " + state_name
    
    return fig_co, fig_oz, fig_no2, fig_so2, fig_pm, recommendation_text, current_location



# Callback for education option    
@app.callback(
    Output(component_id='educate_me', component_property='children'),
    [Input(component_id='education', component_property='value')]
)  
def update_education(topic):
    
    # Information about the AQI
    text_aqi = html.Div([
        html.H2(topic),
        html.Table([
            html.Tr([html.Th('Air Quality Index'),
                     html.Th('Levels of Health Concern'),
                     html.Th('Colors')],style={"background-color": "#dddddd"}),
            html.Tr([html.Td('When the AQI is in this range:'),
                     html.Td('...air quality conditions are:'),
                     html.Td('...as symbolized by this color:')],
                    style={"background-color": "#dddddd", "font-style":"italic"}),
            html.Tr([html.Td('0-50'),
                     html.Td('Good'),
                     html.Td('Green')],style={"background-color": "green"}),
            html.Tr([html.Td('51-100'),
                     html.Td('Moderate'),
                     html.Td('Yellow')],style={"background-color": "yellow"}),
            html.Tr([html.Td('101-150'),
                     html.Td('Unhealthy for Sensitive Groups'),
                     html.Td('Orange')],style={"background-color": "orange"}),
            html.Tr([html.Td('151-200'),
                     html.Td('Unhealthy'),
                     html.Td('Red')],style={"background-color": "red"}),
            html.Tr([html.Td('201-300'),
                     html.Td('Very Unhealthy'),
                     html.Td('Purple')],style={"background-color": "purple"}),
            html.Tr([html.Td('301-500'),
                     html.Td('Harzardous'),
                     html.Td('Maroon')],style={"background-color": "maroon"})
        ]),
        
        html.P("Each category corresponds to a different level of health concern. The six levels of health concern and what they mean are:"),
        html.Ul([
            html.Li("\"Good\" AQI is 0 - 50. Air quality is considered satisfactory, and air pollution poses little or no risk."),
            html.Li("\"Moderate\" AQI is 51 - 100. Air quality is acceptable; however, for some pollutants there may be a moderate health concern for a very small number of people. For example, people who are unusually sensitive to ozone may experience respiratory symptoms."),
            html.Li("\"Unhealthy for Sensitive Groups\" AQI is 101 - 150. Although general public is not likely to be affected at this AQI range, people with lung disease, older adults and children are at a greater risk from exposure to ozone, whereas persons with heart and lung disease, older adults and children are at greater risk from the presence of particles in the air."),
            html.Li("\"Unhealthy\" AQI is 151 - 200. Everyone may begin to experience some adverse health effects, and members of the sensitive groups may experience more serious effects."),
            html.Li("\"Very Unhealthy\" AQI is 201 - 300. This would trigger a health alert signifying that everyone may experience more serious health effects."),
            html.Li("\"Hazardous\" AQI greater than 300. This would trigger health warnings of emergency conditions. The entire population is more likely to be affected."),
        ]),
        html.P("Referenced from https://www.epa.gov/outdoor-air-quality-data/air-data-basic-information", style={"font-style":"italic"})
    ])
    
    # Information about Carbon Monoxide
    text_co = html.Div([
        html.H2("Carbon Monoxide"),
        html.H3("What is CO?"),
        html.P("CO is a colorless, odorless gas that can be harmful when inhaled in large amounts. CO is released when something is burned. The greatest sources of CO to outdoor air are cars, trucks and other vehicles or machinery that burn fossil fuels. A variety of items in your home such as unvented kerosene and gas space heaters, leaking chimneys and furnaces, and gas stoves also release CO and can affect air quality indoors."),
        html.H3("Potential Health Problems"),
        html.P("Breathing air with a high concentration of CO reduces the amount of oxygen that can be transported in the blood stream to critical organs like the heart and brain."),
        html.P("At very high levels, which are  possible indoors or in other enclosed environments, CO can cause dizziness, confusion, unconsciousness and death."),
        html.P("Very high levels of CO are not likely to occur outdoors. However, when CO levels are elevated outdoors, they can be of particular concern for people with some types of heart disease. These people already have a reduced ability for getting oxygenated blood to their hearts in situations where the heart needs more oxygen than usual. They are especially vulnerable to the effects of CO when exercising or under increased stress. In these situations, short-term exposure to elevated CO may result in reduced oxygen to the heart accompanied by chest pain also known as angina."),
        html.P("Referenced from https://www.epa.gov/co-pollution/basic-information-about-carbon-monoxide-co-outdoor-air-pollution#Effects", style={"font-style":"italic"})
    ])
    
    # Information about Ozone
    text_oz = html.Div([
        html.H2("Ground-level Ozone"),
        html.H3("What is \"good\" vs. \"bad\" ozone?"),
        html.P("Ozone is a gas composed of three atoms of oxygen (O3). Ozone occurs both in the Earth's upper atmosphere and at ground level. Ozone can be good or bad, depending on where it is found."),
        html.P("Called stratospheric ozone, good ozone occurs naturally in the upper atmosphere, where it forms a protective layer that shields us from the sun's harmful ultraviolet rays. This beneficial ozone has been partially destroyed by manmade chemicals, causing what is sometimes called a \"hole in the ozone.\" The good news is, this hole is diminishing."),
        html.P("Ozone at ground level is a harmful air pollutant, because of its effects on people and the environment, and it is the main ingredient in \"smog.\""),
        html.H3("Potential Health Problems"),
        html.P("Ozone in the air we breathe can harm our health. People most at risk from breathing air containing ozone include people with asthma, children, older adults, and people who are active outdoors, especially outdoor workers. In addition, people with certain genetic characteristics, and people with reduced intake of certain nutrients, such as vitamins C and E, are at greater risk from ozone exposure."),
        html.P("Breathing elevated concentrations of ozone can trigger a variety of responses, such as chest pain, coughing, throat irritation, and airway inflammation. It also can reduce lung function and harm lung tissue. Ozone can worsen bronchitis, emphysema, and asthma, leading to increased medical care."),
        html.P("Referenced from https://www.epa.gov/ground-level-ozone-pollution/ground-level-ozone-basics", style={"font-style":"italic"})
    ])
    
    # Information about Nitrogen Dioxide
    text_no = html.Div([
        html.H2("Nitrogen Dioxide"),
        html.H3("What is Nitrogen Dioxide and how does it get in the air?"),
        html.P("Nitrogen Dioxide (NO2) is one of a group of highly reactive gases known as oxides of nitrogen or nitrogen oxides (NOx). Other nitrogen oxides include nitrous acid and nitric acid. NO2 is used as the indicator for the larger group of nitrogen oxides."),
        html.P("NO2 primarily gets in the air from the burning of fuel. NO2 forms from emissions from cars, trucks and buses, power plants, and off-road equipment."),
        html.H3("Potential Health Problems"),
        html.P("Breathing air with a high concentration of NO2 can irritate airways in the human respiratory system. Such exposures over short periods can aggravate respiratory diseases, particularly asthma, leading to respiratory symptoms (such as coughing, wheezing or difficulty breathing), hospital admissions and visits to emergency rooms. Longer exposures to elevated concentrations of NO2 may contribute to the development of asthma and potentially increase susceptibility to respiratory infections. People with asthma, as well as children and the elderly are generally at greater risk for  the health effects of NO2."),
        html.P("NO2 along with other NOx  reacts with other chemicals in the air to form both particulate matter and ozone. Both of these are also harmful when inhaled due to effects on the respiratory system."),
        html.P("Referenced from https://www.epa.gov/no2-pollution/basic-information-about-no2#What%20is%20NO2", style={"font-style":"italic"})
        
    ])

    # Information about Sulfur Dioxide
    text_so = html.Div([
        html.H2("Sulfur Dioxide"),
        html.H3("What is SO2 and how does it get in the air?"),
        html.P("EPA’s national ambient air quality standards for SO2 are designed to protect against exposure to the entire group of sulfur oxides (SOx).  SO2 is the component of greatest concern and is used as the indicator for the larger group of gaseous sulfur oxides (SOx).  Other gaseous SOx (such as SO3) are found in the atmosphere at concentrations much lower than SO2. "),
        html.P("Control measures that reduce SO2 can generally be expected to reduce people’s exposures to all gaseous SOx.  This may have the important co-benefit of reducing the formation of particulate sulfur pollutants, such as fine sulfate particles."),
        html.P("Emissions that lead to high concentrations of SO2 generally also lead to the formation of other SOx. The largest sources of SO2 emissions are from fossil fuel combustion at power plants andother industrial facilities. "),
        html.P("The largest source of SO2 in the atmosphere is the burning of fossil fuels by power plants and other industrial facilities. Smaller sources of SO2 emissions include: industrial processes such as extracting metal from ore; natural sources such as volcanoes; and locomotives, ships and other vehicles and heavy equipment that burn fuel with a high sulfur content."),
        html.H3("Potential Health Problems"),
        html.P("Short-term exposures to SO2 can harm the human respiratory system and make breathing difficult. People with asthma, particularly children, are sensitive to these effects of SO2."),
        html.P("SO2 emissions that lead to high concentrations of SO2 in the air generally also lead to the formation of other sulfur oxides (SOx). SOx can react with other compounds in the atmosphere to form small particles. These particles contribute to particulate matter (PM) pollution. Small particles may penetrate deeply into the lungs and in sufficient quantity can contribute to health problems."),
        html.P("Referenced from https://www.epa.gov/so2-pollution/sulfur-dioxide-basics#what%20is%20so2", style={"font-style":"italic"})
        
    ])

    # Information about PM2.5
    text_pm = html.Div([
        html.H2("Particulate Matter"),
        html.H3("What is PM, and how does it get into the air?"),
        html.P("PM stands for particulate matter (also called particle pollution): the term for a mixture of solid particles and liquid droplets found in the air. Some particles, such as dust, dirt, soot, or smoke, are large or dark enough to be seen with the naked eye. Others are so small they can only be detected using an electron microscope."),
        html.P("Particle pollution includes:"),
        html.Ul([
            html.Li("PM10: inhalable particles, with diameters that are generally 10 micrometers and smaller."),
            html.Li("PM2.5: fine inhalable particles, with diameters that are generally 2.5 micrometers and smaller")
        ]),
        html.P("These particles come in many sizes and shapes and can be made up of hundreds of different chemicals."),
        html.P("Some are emitted directly from a source, such as construction sites, unpaved roads, fields, smokestacks or fires."),
        html.P("Most particles form in the atmosphere as a result of complex reactions of chemicals such as sulfur dioxide and nitrogen oxides, which are pollutants emitted from power plants, industries and automobiles."),
        html.H3("Potential Health Problems"),
        html.P("Particulate matter contains microscopic solids or liquid droplets that are so small that they can be inhaled and cause serious health problems. Some particles less than 10 micrometers in diameter can get deep into your lungs and some may even get into your bloodstream. Of these, particles less than 2.5 micrometers in diameter, also known as fine particles or PM2.5, pose the greatest risk to health."),
        html.P("Fine particles are also the main cause of reduced visibility (haze) in parts of the United States, including many of our treasured national parks and wilderness areas."),
        html.P("Referenced from https://www.epa.gov/pm-pollution/particulate-matter-pm-basics#PM", style={"font-style":"italic"})
        
    ])
    
    # Return corresponding text based on selection
    if topic == 'AQI Values':
        return text_aqi
    elif topic == 'Carbon monoxide':
        return text_co
    elif topic == 'Ozone':
        return text_oz
    elif topic == 'Nitrogen dioxide (NO2)':
        return text_no
    elif topic == 'Sulfur dioxide':
        return text_so
    elif topic == 'PM2.5 - Local Conditions':
        return text_pm

    return topic

if __name__ == '__main__':
    app.run_server(debug=False)

