from dash import Dash, dcc, html
from numpy import gradient
import plotly.express as px
import pandas as pd

app = Dash(__name__)

df = pd.read_csv("./all_flex_results.csv")
df['Date'] = pd.to_datetime(df['Date'], format='%m_%d_%Y' )
df['Formulation'] = df['Experiment'].apply(lambda x: x.split('_')[0])
df['Formulation'] = df['Formulation'].apply(lambda x: x.split('-')[0])

fig = px.box(df, x='Formulation', y='flex modulus')

app.layout = html.Div(children=[
    html.H1(
        children='Flexural Modulus Distribution By Date',
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
