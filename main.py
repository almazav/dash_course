import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas  as pd
#######################################################################################################################
#                                                   DATA CLEANING
#######################################################################################################################
#get data from github(saved localy)
confirmed = 'covid/time_series_covid19_confirmed_global.csv'
deaths = 'covid/time_series_covid19_deaths_global.csv'
recovered = 'covid/time_series_covid19_recovered_global.csv'

#read data as dataframes

df_confirmed = pd.read_csv(confirmed)
df_deaths = pd.read_csv(deaths)
df_recovered = pd.read_csv(recovered)

#unpivot data

def df_unpivot(df, col_name):
    """

    :param df:
    :param col_name:
    :return: unpivot dataframe
    """
    dates = df.columns[4:]
    df_melted = df.melt(id_vars=['Province/State','Country/Region','Lat','Long'],
                        value_vars=dates, var_name='date', value_name=col_name)
    return df_melted

total_confirmed = df_unpivot(df_confirmed, 'confirmed')
total_deaths = df_unpivot(df_deaths, 'deaths')
total_recovered = df_unpivot(df_recovered, 'recovered')

#merging dataframes
covid_data =  total_confirmed.merge(right=total_deaths, how='left',on=['Province/State','Country/Region','date','Lat','Long'])
covid_data =  covid_data.merge(right=total_recovered, how='left',on=['Province/State','Country/Region','date','Lat','Long'])

#converting date column from string to date format
covid_data['date'] = pd.to_datetime(covid_data['date'])

#fill nan values with 0

covid_data['recovered'] = covid_data['recovered'].fillna(0)

#create active column

covid_data['active'] = covid_data['confirmed'] - (covid_data['deaths']+covid_data['recovered'])

covid_data_1 = covid_data.groupby(['date'])[['confirmed','deaths','recovered','active']].sum().reset_index()



#######################################################################################################################
#                                       DASHBOARD
#######################################################################################################################

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Div([
            html.Img(src=app.get_asset_url('/logo.jpg'),
                     id='logo',
                     style={'height': '60px',
                            'width': 'auto',
                            'margin-bottom': '25px'})

        ], className='one-third column'),
        html.Div([
            html.Div([
                html.H3('Covid - 19',style= {'margin-bottom': '0px', 'color':'white'}),
                html.H5('Track Covid - 19 Cases',style= {'margin-bottom': '0px', 'color':'white'})
            ])

        ],className = 'one-half-column', id ='title'),

        html.Div([
            html.H6('Last Updated: ' + str(covid_data['date'].iloc[-1].strftime(('%B %d %Y'))) + ' 00:01 (UTC)'
                    ,style={'color':'orange'})

        ],className = 'one-third column', id = 'title1')

    ], id='header', className='row flex-display', style={'margin-bottom': '25px'}),

    html.Div([
        html.Div([
            html.H6(children='Global cases',
                    style= {'textAlign':'center',
                            'color': 'white'}),
            html.P(f"{covid_data_1['confirmed'].iloc[-1]:.0f}",
                   style={'textAlign': 'center',
                          'color': 'orange',
                          'fontSize':40}
        ),
            html.P("new: "+ f"{(covid_data_1['confirmed'].iloc[-1]- covid_data_1['confirmed'].iloc[-2]):.0f}"
                   + " (" + str(round((covid_data_1['confirmed'].iloc[-1]- covid_data_1['confirmed'].iloc[-2])/
                                      (covid_data_1['confirmed'].iloc[-1]) * 100, 2)) +"%)",
                   style={'textAlign':'center',
                          'color':'orange',
                          'fontSize':15,
                          'margin-top':'-18px'})

        ], className='card_container three columns'),
        html.Div([
            html.H6(children='Global Deaths',
                    style={'textAlign': 'center',
                           'color': 'white'}),
            html.P(f"{covid_data_1['deaths'].iloc[-1]:.0f}",
                   style={'textAlign': 'center',
                          'color': '#dd1e35',
                          'fontSize': 40}
                   ),
            html.P("new: " + f"{(covid_data_1['deaths'].iloc[-1] - covid_data_1['deaths'].iloc[-2]):.0f}"
                   + " (" + str(round((covid_data_1['deaths'].iloc[-1] - covid_data_1['deaths'].iloc[-2]) /
                                      (covid_data_1['deaths'].iloc[-1]) * 100, 2)) + "%)",
                   style={'textAlign': 'center',
                          'color': '#dd1e35',
                          'fontSize': 15,
                          'margin-top': '-18px'})

        ], className='card_container three columns'),
        html.Div([
            html.H6(children='Global Recovered',
                    style={'textAlign': 'center',
                           'color': 'white'}),
            html.P(f"{covid_data_1['recovered'].iloc[-1]:.0f}",
                   style={'textAlign': 'center',
                          'color': 'green',
                          'fontSize': 40}
                   ),
            html.P("new: " + f"{(covid_data_1['recovered'].iloc[-1] - covid_data_1['recovered'].iloc[-2]):.0f}"
                   + " (" + str(round((covid_data_1['recovered'].iloc[-1] - covid_data_1['recovered'].iloc[-2]) /
                                      (covid_data_1['recovered'].iloc[-1]) * 100, 2)) + "%)",
                   style={'textAlign': 'center',
                          'color': 'green',
                          'fontSize': 15,
                          'margin-top': '-18px'})

        ], className='card_container three columns'),
        html.Div([
            html.H6(children='Global Active',
                    style={'textAlign': 'center',
                           'color': 'white'}),
            html.P(f"{covid_data_1['active'].iloc[-1]:.0f}",
                   style={'textAlign': 'center',
                          'color': '#e55467',
                          'fontSize': 40}
                   ),
            html.P("new: " + f"{(covid_data_1['active'].iloc[-1] - covid_data_1['active'].iloc[-2]):.0f}"
                   + " (" + str(round((covid_data_1['active'].iloc[-1] - covid_data_1['active'].iloc[-2]) /
                                      (covid_data_1['active'].iloc[-1]) * 100, 2)) + "%)",
                   style={'textAlign': 'center',
                          'color': '#e55467',
                          'fontSize': 15,
                          'margin-top': '-18px'})

        ], className='card_container three columns')

    ], className='row flex display'),
    html.Div([
        html.Div([
            html.P('Select Country:', className='fix_label',style={'color':'white'}),
            dcc.Dropdown(id ='w_countries',
                         multi=False,
                         searchable=True,
                         value='US',
                         placeholder='Select Countries',
                         options=[{'label':c,'value':c}
                                  for c in (covid_data['Country/Region'].unique())],className='dcc_compon'),
            html.P('New Cases: ' + ' ' + str(covid_data['date'].iloc[-1].strftime('%B %d %Y')),
                   className='fix_label', style={'test-align': 'center','color':'white'}),
            dcc.Graph(id= 'confirmed',config={'displayModeBar':False}, className='dcc_compon',
                      style={'margin-top':'20px'})

        ],className='create_container three columns')
    ], className='row flex display')
], id='mainContainer',style={'display': 'flex', 'flex-direction':'column'})

@app.callback(Output('confirmed','figure'),
              [Input('w_countries','value')])
def update_confirmed(w_countries):
    covid_data_2 = covid_data.groupby(['date', 'Country/Region'])[
        ['confirmed', 'deaths', 'recovered', 'active']].sum().reset_index()
    value_confirmed = covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-1] - \
                      covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-2]
    delta_confirmed = covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-2] - \
                      covid_data_2[covid_data_2['Country/Region'] == w_countries]['confirmed'].iloc[-3]

    return {
        'data':[go.Indicator(
            mode='number+delta',
            value=value_confirmed,
            delta={'reference':delta_confirmed,
                   'position':'right',
                   'valueformat':',g',
                   'relative':False,
                   'font':{'size':15}},
            number={'valueformat': ',',
                    'font' : {'size':20}},
            domain={'y': [0, 1], 'x':[0, 1]}
        )],
        'layout':go.Layout(
            title={'text':'New Conirmed',
                   'y':1,
                   'x': 0.5,
                   'xanchor': 'center',
                   'yanchor': 'top'},
            font=dict(color= 'orange'),
            paper_bgcolor='#1f2c56',
            plot_bgcolor='#1f2c56',
            height=50,
        )
    }

if __name__== '__main__':
    app.run_server(debug=True)