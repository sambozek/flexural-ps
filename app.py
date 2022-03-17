# from tokenize import group
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine

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


conn = create_engine('postgresql://doadmin:RGUuvzY6n25TQF5E@cor-properties-do-user-3715075-0.b.db.ondigitalocean.com:25060/physical_properties?sslmode=require')
df_flex = pd.read_sql('flexural_data', conn)


df_flex['Date'] = pd.to_datetime(df_flex['Date'], format='%m_%d_%Y')
df_flex['Formulation'] = df_flex['Experiment'].apply(
    lambda x: x.split('_')[0])

df_flex['Formulation'] = df_flex['Formulation'].apply(
    lambda x: x.split('-')[0])

df_flex2, meds_flex = group_sort_by_formulation(
    df_flex,
    "Formulation",
    'flex modulus')

fig_flex = px.box(
    df_flex2,
    x='Formulation',
    y='flex modulus',
    points='all',
    category_orders={'Formulation': meds_flex.index}
    )

df_tens = pd.read_sql('tensile_data', conn)

df_tens['Date'] = pd.to_datetime(df_tens['Date'], format='%Y-%m-%d')
df_tens['gen_formulation'] = df_tens['gen_formulation'].apply(
    lambda x: x.replace("A1", "A.1"))
df_tens['gen_formulation'].replace('.+?(?=-)', '', regex=True, inplace=True)
df_tens['gen_formulation'].replace('.+?(?= )', '', regex=True, inplace=True)

df_tens_aseries = df_tens[df_tens['gen_formulation'].str.contains('A.')]


df_tens2, meds_tens = group_sort_by_formulation(
    df_tens_aseries,
    "gen_formulation",
    'Break_Strain'
    )

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
            'textAlign': 'Center'
        }
    ),
    dcc.Graph(
        id='By-Formulation-Flex',
        figure=fig_flex
    ),
    html.H1(
        children='Elongation at Break Distribution By Median',
        style={
            'textAlign': 'Center'
        }
    ),
    dcc.Graph(
        id='By-Formulation',
        figure=fig_tens
    ),
    html.H1(
        children="Formulation Physical Properties",
        style={
            'textAlign': 'Center'
        }),
    html.Div(
        dcc.Dropdown(
            list(set(
                df_tens_aseries['gen_formulation'].unique()
                    ).intersection(df_flex['Formulation'].unique())
                ),
                id= 'formulation-id'
                    )
            ),
    dcc.Graph()
])

@app.callback(
    Output('formuation-fig', 'figure'),
    Input('formulation-id', 'value')
)
def update_graph(formulation_id):
    df_tens_aseries[df_tens_aseries['gen_formulation'] == formulation_id]
    df_flex2[df_flex2['formulation'] == formulation_id]

if __name__ == '__main__':
    app.run_server(debug=True)
