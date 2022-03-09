# from tokenize import group
from dash import Dash, dcc, html
from numpy import gradient
import plotly.express as px
import pandas as pd

app = Dash(__name__)

server = app.server


def group_sort_by_formulation(df, group_col, target_column):
    df_grouped = df.groupby(group_col)
    df_meds = pd.DataFrame(
        {col: vals[target_column] for col, vals in df_grouped})

    meds = df_meds.median()
    meds.sort_values(ascending=False, inplace=True)

    df_meds = df_meds[meds.index]
    sorted_df = df.sort_values(by=[group_col], ascending=False)
    return sorted_df, meds


df_flex = pd.read_csv("https://gist.githubusercontent.com/sambozek/8b3af6bbc873402ae7b5678d30c5c8b2/raw/b5445235ab7139b36283d4ee987a3969b6014425/flex_0218.csv")


df_flex['Date'] = pd.to_datetime(df_flex['Date'], format='%m_%d_%Y')
df_flex['Formulation'] = df_flex['Experiment'].apply(lambda x: x.split('_')[0])
df_flex['Formulation'] = df_flex['Formulation'].apply(lambda x: x.split('-')[0])

df_flex2, meds_flex = group_sort_by_formulation(df_flex, "Formulation", 'flex modulus')

# df_flex_grouped = df_flex.groupby(["Formulation"])
# df_flex_meds = pd.DataFrame(
#     {col:vals['flex modulus'] for col, vals in df_flex_grouped})

# meds = df_flex_meds.median()
# meds.sort_values(ascending=False, inplace=True)

# df_flex_meds = df_flex_meds[meds.index]
# df_flex2 = df_flex.sort_values(by=['Formulation'], ascending=False)
fig_flex = px.box(
    df_flex2,
    x='Formulation',
    y='flex modulus',
    points='all',
    category_orders={'Formulation': meds_flex.index}
    )

df_tens = pd.read_csv("https://gist.githubusercontent.com/sambozek/050253cb59f7cb9284c41981ed1d6be3/raw/e8dee4f7f87f9b1937e0d001ada58bf241f8a6a9/tens.csv")

df_tens['Date'] = pd.to_datetime(df_tens['Date'], format='%Y-%m-%d')
df_tens['gen_formulation'] = df_tens['gen_formulation'].apply(lambda x: x.replace("A1", "A.1"))
df_tens['gen_formulation'].replace('.+?(?=-)','', regex=True, inplace=True)
df_tens['gen_formulation'].replace('.+?(?= )', '', regex=True, inplace=True)

df_tens_aseries = df_tens[df_tens['gen_formulation'].str.contains('A.')]


df_tens2, meds_tens = group_sort_by_formulation(df_tens_aseries, "gen_formulation", 'Break_Strain')
fig_tens = px.box(
    df_tens2,
    x='gen_formulation',
    y='Break_Strain',
    points='all',
    category_orders={'gen_formulation': meds_tens.index}
    )

app.layout = html.Div(children=[
    html.H1(
        children='Flexural Modulus Distribution By Median',
        style={
            'textAlign':'Center'
        }
    ),
    dcc.Graph(
        id='By-Formulation-Flex',
        figure=fig_flex
    ),
    html.H1(
        children='Elongation at Break Distribution By Median',
        style={
            'textAlign':'Center'
        }
    ),
    dcc.Graph(
        id='By-Formulation',
        figure=fig_tens
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True)
