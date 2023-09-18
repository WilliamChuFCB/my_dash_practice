from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import pycountry_convert as pc

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# define dash app and utilize an external style sheet
app = Dash(__name__, external_stylesheets=external_stylesheets)

# data reading and preprocessing
df = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')
df_wide = df.pivot(index=['Country Name', 'Year'], columns='Indicator Name', values='Value').reset_index()
df_wide = df_wide.loc[~df_wide['Population density (people per sq. km of land area)'].isna(),:].reset_index()
df_wide.drop('index', axis=1, inplace=True)

# add a continent column to the dataset
def country_to_continent(country_name):
    country_alpha2 = pc.country_name_to_country_alpha2(country_name)
    country_continent_code = pc.country_alpha2_to_continent_code(country_alpha2)
    country_continent_name = pc.convert_continent_code_to_continent_name(country_continent_code)
    return country_continent_name
Continent = []
for i in range(len(df_wide)):
    try:
        Continent.append(country_to_continent(df_wide.loc[i,'Country Name']))
    except:
        Continent.append('Unknown')
df_wide['Continent'] = Continent

# create a new dataframe with shorter column names
df_rename = df_wide.copy(deep=True)
df_rename.columns = ['Country', 'Year', 'Agriculture, value added',
       'CO2 emissions',
       'Domestic credit',
       'Electric consumption',
       'Energy use',
       'Exports',
       'Fertility rate', 'GDP growth',
       'Imports',
       'Industry, value added',
       'Inflation',
       'Life expectancy',
       'Population density',
       'Services, value added', 'Continent']

# define some markdown text in the tabs
markdown_tab1 = '''
**Note:** 
- *In this page, you can choose different combinations of variables to create a scatter plot*
- *Two time series plots on the right will update automatically when you hover over points in the scatter plot*
'''

markdown_tab2 = '''
**Note:**
- *In this page, you can further explore the relationship among variables*
- *You can choose multiple input variables (>1) to create a scatter-matrix plot*
'''

markdown_tab3 = '''
**Note:**
- *In this page, you will find three different animation plots displaying the relationship of CO2 emissions with several other variables*
- *A scatter plot, a box plot, and a 3D scatter plot are included in this page*
'''

# define the content within tab1
tab1_content = html.Div([
    dcc.Markdown(markdown_tab1),
    html.Div([
        html.Div([
            dcc.Dropdown(
                df['Indicator Name'].unique(),
                'Population density (people per sq. km of land area)',
                id='crossfilter-xaxis-name',
            ),
            dcc.RadioItems(
                ['Linear', 'Log'],
                'Log',
                id='crossfilter-xaxis-type',
                labelStyle={'display': 'inline-block', 'marginTop': '5px'}
            )
        ],
        style={'width': '49%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                df['Indicator Name'].unique(),
                'Fertility rate, total (births per woman)',
                id='crossfilter-yaxis-name'
            ),
            dcc.RadioItems(
                ['Linear', 'Log'],
                'Linear',
                id='crossfilter-yaxis-type',
                labelStyle={'display': 'inline-block', 'marginTop': '5px'}
            )
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'padding': '10px 5px'
    }),

    html.Div([
        dcc.Graph(
            id='crossfilter-hover',
            hoverData={'points': [{'customdata': ['United States']}]}
        )
    ], style={'width': '49%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(id='x-time-series'),
        dcc.Graph(id='y-time-series'),
    ], style={'display': 'inline-block', 'width': '49%'}),

    html.Div(dcc.Slider(
        df['Year'].min(),
        df['Year'].max(),
        step=None,
        id='crossfilter-year-slider',
        value=df['Year'].max(),
        marks={str(year): str(year) for year in df['Year'].unique()}
    ), style={'width': '39%', 'padding': '0px 20px 20px 20px'})
])

# define the content within tab2
tab2_content = html.Div([
    dcc.Markdown(markdown_tab2),
    dcc.Dropdown(
        df_rename.columns[2:-1],
        ['Life expectancy', 'Fertility rate'],
        multi=True,
        id='multi-dropdown'
    ),
    dcc.Graph(id='scatter-matrix')
])

# define three animation plots that will be put in tab3
fig1 = px.scatter(df_wide, x='CO2 emissions (metric tons per capita)', y='GDP growth (annual %)',
                                size='Population density (people per sq. km of land area)', 
                                animation_frame='Year', animation_group='Country Name', 
                                hover_name='Country Name', color='Continent',
                                size_max=55, title='Animation Scatter Plot')

fig1.update_layout(width=800, height=375)
fig1.update_layout(showlegend=False)

fig2 = px.scatter_3d(df_rename, x='Life expectancy', y='Fertility rate', z='CO2 emissions',
                     hover_name='Country', color='Continent', animation_frame='Year',
                    title='3D Scatter Plot')
fig2.update_layout(width=700, height=750)
fig2.update_layout(transition=dict(duration=100))

fig3 = px.box(df_rename, x='Continent', y='CO2 emissions', animation_frame='Year',
              color='Continent', hover_name='Country', range_y=[0,30],
              title='Animation Box Plot')
fig3.update_layout(width=800, height=375)
fig3.update_layout(showlegend=False)
fig3.update_layout(transition=dict(duration=100))

# define the content within tab3
tab3_content = html.Div([
    dcc.Markdown(markdown_tab3),
    html.Div([
        dcc.Graph(figure=fig1),
        dcc.Graph(figure=fig3)
    ], style={'width': '54%', 'display': 'inline-block'}),
    
    html.Div([
        dcc.Graph(figure=fig2)
    ], style={'width': '44%', 'display': 'inline-block'}),
    
])

# define the app layout which contains three tabs
app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Tab 1', value='tab-1'),
        dcc.Tab(label='Tab 2', value='tab-2'),
        dcc.Tab(label='Tab 3', value='tab-3'),
    ]),
    html.Div(id='tab-1-content', children=tab1_content), 
    html.Div(id='tab-2-content', children=tab2_content, style={'display': 'none'}),
    html.Div(id='tab-3-content', children=tab3_content, style={'display': 'none'})
])

# define the callbacks
@callback(
    [Output('tab-1-content', 'style'),
     Output('tab-2-content', 'style'),
     Output('tab-3-content', 'style')],
    Input('tabs', 'value')
)
def update_tabs(tab):
    style_to_show = {'display': 'block'}
    style_to_hide = {'display': 'none'}

    if tab == 'tab-1':
        return style_to_show, style_to_hide, style_to_hide
    elif tab == 'tab-2':
        return style_to_hide, style_to_show, style_to_hide
    else:
        return style_to_hide, style_to_hide, style_to_show

@callback(
    Output('crossfilter-hover', 'figure'),
    Input('crossfilter-xaxis-name', 'value'),
    Input('crossfilter-yaxis-name', 'value'),
    Input('crossfilter-xaxis-type', 'value'),
    Input('crossfilter-yaxis-type', 'value'),
    Input('crossfilter-year-slider', 'value'))
def update_graph1(xaxis_column_name, yaxis_column_name, xaxis_type, yaxis_type, year_value):
    dff = df_wide[df_wide['Year'] == year_value]
    fig = px.scatter(dff, x=xaxis_column_name, y=yaxis_column_name,
            hover_name='Country Name', color='Continent', custom_data=[dff['Country Name']]
            )
    fig.update_xaxes(title=xaxis_column_name, type='linear' if xaxis_type == 'Linear' else 'log')
    fig.update_yaxes(title=yaxis_column_name, type='linear' if yaxis_type == 'Linear' else 'log')
    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')
    return fig

# define a function to create time series plots
def create_time_series(dff, axis_type, title, axis_name):
    fig = px.scatter(dff, x='Year', y=axis_name)
    fig.update_traces(mode='lines+markers')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(type='linear' if axis_type == 'Linear' else 'log')
    fig.update_layout(yaxis_title='Value')
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       text=title)
    fig.update_layout(height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})
    return fig

@callback(
    Output('x-time-series', 'figure'),
    Input('crossfilter-hover', 'hoverData'),
    Input('crossfilter-xaxis-name', 'value'),
    Input('crossfilter-xaxis-type', 'value'))
def update_x_timeseries(hoverData, xaxis_column_name, axis_type):
    country_name = hoverData['points'][0]['customdata'][0]
    dff = df_wide[df_wide['Country Name'] == country_name]
    title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    return create_time_series(dff, axis_type, title, xaxis_column_name)

@callback(
    Output('y-time-series', 'figure'),
    Input('crossfilter-hover', 'hoverData'),
    Input('crossfilter-yaxis-name', 'value'),
    Input('crossfilter-yaxis-type', 'value'))
def update_y_timeseries(hoverData, yaxis_column_name, axis_type):
    country_name = hoverData['points'][0]['customdata'][0]
    dff = df_wide[df_wide['Country Name'] == country_name]
    return create_time_series(dff, axis_type, yaxis_column_name, yaxis_column_name)

@callback(
    Output('scatter-matrix', 'figure'),
    Input('multi-dropdown', 'value')
)
def update_scatter_matrix(value):
    fig = px.scatter_matrix(df_rename, dimensions=value, color='Continent', hover_name='Country')
    fig.update_layout(
    title={
        'text': 'Scatter Matrix Plot of Multiple Variables',
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top'})
    fig.update_traces(diagonal_visible=False)
    fig.update_layout(width=1500, height=640)
    return fig

if __name__ == '__main__':
    app.run(debug=True)








