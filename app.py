from dash import Dash, dcc, html
from numpy import gradient
import plotly.express as px
import pandas as pd

app = Dash(__name__)

server = app.server

df = pd.read_csv("https://gist.githubusercontent.com/sambozek/8b3af6bbc873402ae7b5678d30c5c8b2/raw/b5445235ab7139b36283d4ee987a3969b6014425/flex_0218.csv")
df['Date'] = pd.to_datetime(df['Date'], format='%m_%d_%Y' )
df['Formulation'] = df['Experiment'].apply(lambda x: x.split('_')[0])
df['Formulation'] = df['Formulation'].apply(lambda x: x.split('-')[0])

df_grouped = df.groupby(["Formulation"])
df_meds = pd.DataFrame({col:vals['flex modulus'] for col, vals in df_grouped})

meds = df_meds.median()
meds.sort_values(ascending=False, inplace=True)

df_meds = df_meds[meds.index]
df2 = df.sort_values(by=['Formulation'], ascending=False)
fig = px.box(df2, x='Formulation', y='flex modulus', points='all', category_orders={'Formulation': meds.index})

app.layout = html.Div(children=[
    html.H1(
        children='Flexural Modulus Distribution By Median',
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
