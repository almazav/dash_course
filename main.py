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
        html.Div([], className='card_container three columns')
    ], className='row flex display')
], id='mainContainer',style={'display': 'flex', 'flex-direction':'column'})

if __name__== '__main__':
    app.run_server(debug=True)