from flask import Flask
from flask import render_template
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

app = Flask(__name__)

@app.route("/")
def plotView():

    plt.switch_backend('Agg')

    url = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'

    df = pd.read_csv(url)
    
    #Filter by Australia
    aus_df = df.loc[(df['Country/Region'] == 'Australia')]

    #Sum all states
    aus_df = aus_df.groupby(['Country/Region']).sum()

    #Remove Lat and Long columns
    aus_df.drop(['Lat','Long'], axis=1, inplace=True)

    #Show the difference between days (new cases)
    #aus_df = aus_df.diff(axis=1)

    #Transpose data (days as rows instead of columns)
    aus_df = aus_df.T

    aus_df['New Cases'] = aus_df['Australia'] - aus_df['Australia'].shift(1)

    #Reset the index
    aus_df = aus_df.reset_index()

    aus_df.rename(columns={'index':'Date'}, inplace=True)


    #Convert from string to datetime
    aus_df['Date'] = pd.to_datetime(aus_df['Date'])
    
    #Set beginning of data
    aus_df = aus_df[(aus_df['Date'] > '03-10-2020')]

    #Format date
    aus_df['Date'] = aus_df['Date'].dt.strftime('%d/%m')


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
    title_text="New and Overall Cases in Australia"
    )

    # Set x-axis title
    fig.update_xaxes(title_text="Date")

    # Set y-axes titles
    fig.update_yaxes(title_text="New Cases", secondary_y=False)
    fig.update_yaxes(title_text="Total Cases", secondary_y=True)

    # fig.savefig('./static/images/aus_new.png')
    fig.write_html("./templates/file.html")
    # fig.write_html("./index.html")


   
    return render_template('file.html') #, url ='/static/images/aus_new.png')
