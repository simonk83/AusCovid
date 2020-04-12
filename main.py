from flask import Flask
from flask import render_template
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

app = Flask(__name__)

@app.route("/")
def plotView():

    plt.switch_backend('Agg')

    sns.set(rc={'figure.figsize':(22,8)})

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

    # fig = px.bar(aus_df, x='Date', y='New Cases')
    # fig = go.Figure([go.bar(x=aus_df['Date'], y=aus_df['New Cases'])])

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


    # #Set graph options
    # plt.style.use('seaborn-darkgrid')
    # palette = plt.get_cmap('Set1')
    # plt.figure(figsize=(20,10))
        
    # # #Plot the graph    
    # # plt.plot(aus_df['index'], aus_df['Australia'], marker = '', color=palette(1), linewidth=1.9, alpha=0.9, label='Australia')

    # # #Set the title
    # # plt.title('Australia', loc='left', fontsize=12, fontweight=0, color=palette(1))

    # # #Name the axis  
    # # plt.text(16, -60, 'Date',horizontalalignment='center', verticalalignment='center')
    # # plt.text(-2.4, 280, 'New Cases', horizontalalignment='center', verticalalignment='center', rotation='vertical')

    # aus_df.set_index('Date', inplace=True)

    # ax = aus_df[['New Cases']].plot(kind='bar', title ="Australia", figsize=(15, 10), legend=False)
    # ax2 = aus_df['Australia'].plot(secondary_y=True)

    # ax.set_xlabel("Date", fontsize=12)
    # ax.set_ylabel("New Cases", fontsize=12)
    # ax2.set_ylabel("Total Cases", fontsize=12)
    # ax2.grid(False)
    # ax.set_xticklabels(ax.get_xticklabels(),rotation=45)


    # plt.savefig('./static/images/aus_new.png')

    
    # Convert plot to PNG image
    # pngImage = io.BytesIO()
    # FigureCanvas(plt).print_png(pngImage)
    
    # # Encode PNG image to base64 string
    # pngImageB64String = "data:image/png;base64,"
    # pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
    
    return render_template('file.html') #, url ='/static/images/aus_new.png')
