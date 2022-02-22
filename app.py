from dash import Dash, dcc, html
from numpy import gradient
import plotly.express as px
import pandas as pd

app = Dash(__name__)

server = app.server

df = pd.read_csv("https://gist.githubusercontent.com/sambozek/8b3af6bbc873402ae7b5678d30c5c8b2/raw/963c30fd0d87c09da1f71cf352fdeae6a3e8afdd/flex_0218.csv")
df['Date'] = pd.to_datetime(df['Date'], format='%m_%d_%Y' )
df['Formulation'] = df['Experiment'].apply(lambda x: x.split('_')[0])
df['Formulation'] = df['Formulation'].apply(lambda x: x.split('-')[0])
df2 = df.sort_values(by=['Formulation'], ascending=False)
fig = px.box(df2, x='Formulation', y='flex modulus', points='all')

app.layout = html.Div(children=[
    html.H1(
        children='Flexural Modulus Distribution By Formulation',
        style={
            'textAlign':'Center'
        }
    ),
    dcc.Graph(
        id='By-Date',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
