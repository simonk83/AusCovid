from flask import Flask
from flask import render_template
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route("/")
def plotView():

    plt.switch_backend('Agg')

    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    cc_url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv'

    df = pd.read_csv(url)
    dfc = pd.read_csv(cc_url)

    #Filter by Australia
    aus_df = df.loc[(df['Country/Region'] == 'Australia')]

    aus_dfc = dfc.loc[(dfc['Country_Region'] == 'Australia')]
    aus_dfc = aus_dfc.drop(['Lat','Long_', 'People_Tested', 'People_Hospitalized', 'Mortality_Rate', 'UID', 'ISO3', 'Deaths', 'Recovered', 'Active', 'Incident_Rate'], axis=1)
    aus_dfc.rename(columns={'Country_Region':'Country/Region'}, inplace=True)

    #Convert to date, assign to variable, drop column
    aus_dfc['Last_Update'] = pd.to_datetime(aus_dfc['Last_Update'])
    updatetime = aus_dfc['Last_Update'].dt.tz_localize('utc').dt.tz_convert('Australia/Melbourne')
    updatetime = updatetime.dt.tz_localize(None)
    updatetime = updatetime.values[0]
    updatetime = pd.to_datetime(updatetime)
    aus_dfc = aus_dfc.drop(['Last_Update'], axis=1)

    #Sum all states
    aus_df = aus_df.groupby(['Country/Region']).sum()

    #Remove Lat and Long columns
    aus_df.drop(['Lat','Long'], axis=1, inplace=True)

    aus_df = pd.merge(aus_df, aus_dfc, on='Country/Region')
    aus_df = aus_df.groupby(['Country/Region']).sum()

    #Show the difference between days (new cases)
    #aus_df = aus_df.diff(axis=1)

    #Transpose data (days as rows instead of columns)
    aus_df = aus_df.T

    #Show the difference between days (new cases)
    aus_df['New Cases'] = aus_df['Australia'] - aus_df['Australia'].shift(1)

    test = datetime.strftime(datetime.today() - timedelta(1), '%-m/%-d/%y')
    test2 = aus_df.index[-2]

    if aus_df.index[-2] < datetime.strftime(datetime.today() - timedelta(1), '%-m/%-d/%y'):
        aus_df.rename({aus_df.index[-1]: datetime.strftime(datetime.today() - timedelta(1), '%-m/%-d/%y')}, inplace=True)
        aus_df.index = pd.to_datetime(aus_df.index)
    else: 
        aus_df.rename({aus_df.index[-1]: datetime.today()}, inplace=True)
        aus_df.index = pd.to_datetime(aus_df.index)

    #Reset the index
    aus_df = aus_df.reset_index()

    #Rename the Date column
    aus_df.rename(columns={'index':'Date'}, inplace=True)

    #Convert from string to datetime
    aus_df['Date'] = pd.to_datetime(aus_df['Date'])
    
    #Set beginning of data
    aus_df = aus_df[(aus_df['Date'] > '02-29-2020')]

    #Format date
    aus_df['Date'] = aus_df['Date'].dt.strftime('%d/%m')

    #Prepare for secondary Y axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add traces
    fig.add_trace(
        go.Bar(x=aus_df['Date'], y=aus_df['New Cases'], name="New Cases"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=aus_df['Date'], y=aus_df['Australia'], name="Total Cases"),
        secondary_y=True,
    )

    # Add figure title
    fig.update_layout(
    title_text="New and Overall Cases in Australia (data from Johns Hopkins, last updated {})".format(updatetime)
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Date")

    # Set y-axes titles
    fig.update_yaxes(title_text="New Cases", secondary_y=False)
    fig.update_yaxes(title_text="Total Cases", secondary_y=True)

    # fig.update_xaxes(
    # rangeslider_visible=True,
    #     rangeselector=dict(
    #         buttons=list([
    #             dict(count=1, label="1m", step="month", stepmode="backward"),
    #             dict(count=6, label="6m", step="month", stepmode="backward"),
    #             dict(count=1, label="YTD", step="year", stepmode="todate"),
    #             dict(count=1, label="1y", step="year", stepmode="backward"),
    #             dict(step="all")
    #         ])
    #     )
    # )

    fig.layout.template = 'plotly_white'
    fig.write_html("./templates/file.html")
    # fig.write_html("./index.html")


    return render_template('file.html') #, url ='/static/images/aus_new.png')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')