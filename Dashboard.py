import plotly.express as px
import pandas as pd
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

df = pd.read_csv("https://github.com/datenlabor01/multioda/blob/main/DEU%20MultiODA.csv?raw=true")

app = Dash(external_stylesheets = [dbc.themes.ZEPHYR])

df.Year = df.Year.astype(str)

jahr_dropdown = dcc.Dropdown(options = df["Year"].unique(), value="All", style = {"textAlign": "center"}, clearable=True, multi=True,
                                placeholder='Default: Alle Jahre')

organisation_dropdown = dcc.Dropdown(id = "organisation", options = sorted(df["Art der Organisation"].unique()),
                                value="All", style = {"textAlign": "center"}, clearable=True, multi=True,
                                searchable= True, placeholder='Kategorie auswählen')

name_dropdown = dcc.Dropdown(id = "name", options = sorted(df["Organisation"].unique()),
                                value="All", style = {"textAlign": "center"}, clearable=True, multi=True,
                                searchable= True, placeholder='Organisation auswählen')

finanzart = dcc.Slider(id = "finance", min = 0, max = 2, step=1,
                         marks= {0: "Alles", 1: "non-core/bilateral", 2: "core/multilateral"},
                         value = 0, included=False)

wert_dropdown = dcc.Dropdown(options = ["Zusage", "Auszahlung"], value="Zusage", style = {"textAlign": "center"},
                              clearable=False, placeholder='Default: Zusage in USD')

melder_dropdown = dcc.Dropdown(options = sorted(df["Melder"].unique()), value = "All", style = {"textAlign": "center"},
                               clearable=True, multi=True, searchable= True, placeholder='Melder auswählen')

app.layout = html.Div([
     dbc.Row([
         html.H1(children='Dashboard Multilaterale ODA', style={'textAlign': 'center'})
      ]),

    dbc.Row([
        dbc.Col([
        melder_dropdown, html.Br(), wert_dropdown, html.Br()
        ], width=6)], justify = "center"),

    dcc.Tabs([
        dcc.Tab(label='Gesamtüberblick', children=[
            dbc.Row([
                dbc.Col([html.Br(), jahr_dropdown, html.Br(),
                         finanzart], width=6)], justify = "center"),
            dbc.Row([
                dcc.Graph(id='pie', style={'textAlign': 'center'}),
                ]),

            dbc.Row([
                dcc.Graph(id='map', style={'textAlign': 'center'}),
                ]),
            ]),

        dcc.Tab(label='Nach Organisationen', children=[
            dbc.Row([
                dbc.Col([
                    html.Br(), organisation_dropdown, html.Br(), name_dropdown], width=6)], justify="center"),
            dbc.Row([
                dcc.Graph(id = "bar", style={"textAlign": "center"}),
                dcc.Graph(id='bar_2', style={'textAlign': 'center'}),
                ]),
            ]),
    ]),
])

@app.callback(
    Output("organisation", "options"),
    [Input(melder_dropdown, 'value'), Input(jahr_dropdown, "value")]
    )

def fininstrument_options(melder, jahr):
    if (melder == "All") | (melder == []):
      dat_fil = df
    else:
      dat_fil = df[df["Melder"].isin(melder)]

    if (jahr != "All") & (jahr != []):
      dat_fil = dat_fil[dat_fil["Year"].isin(jahr)]

    return sorted(dat_fil['Art der Organisation'].unique())

@app.callback(
    [Output("finance", "marks"), Output("finance", "max"), Output("finance", 'value')],
    [Input(melder_dropdown, 'value'), Input("organisation", "value"),
     Input(wert_dropdown, "value"), Input(jahr_dropdown, "value")],
    )

def fininstrument(melder, organisation, wert, jahr):
    if (melder == "All") | (melder == []):
      dat_fil = df
    else:
      dat_fil = df[df["Melder"].isin(melder)]

    if (organisation != "All") & (organisation != []):
      dat_fil = dat_fil[dat_fil["Art der Organisation"].isin(organisation)]

    if (jahr != "All") & (jahr != []):
      dat_fil = dat_fil[dat_fil["Year"].isin(jahr)]

    dat_fil = dat_fil[dat_fil.wert > 0]

    slider_txt = dat_fil["ODA-Art"].unique()
    slider_txt = slider_txt.tolist()
    slider_txt.insert(0, "Alles")
    marks_slider = {i: slider_txt[i] for i in range(0,  len(slider_txt))}
    max_slider = len(slider_txt)-1
    slider_value = 0
    return marks_slider, max_slider, slider_value

@app.callback(
    Output("name", "options"),
    [Input(melder_dropdown, 'value'), Input("organisation", 'value'), Input(jahr_dropdown, "value")],
    )

def organisation(melder, organisation, jahr):
  if (melder == "All") | (melder == []):
    dat_fil = df
  else:
    dat_fil = df[df["Melder"].isin(melder)]
  if (organisation != "All") & (organisation != []):
    dat_fil = dat_fil[dat_fil["Art der Organisation"].isin(organisation)]
  dat_fil = dat_fil[dat_fil["Year"].isin(jahr)]

  return sorted(dat_fil['Organisation'].unique())

@app.callback(
    [Output('pie', 'figure'), Output("bar", "figure"),
     Output("map", "figure"), Output("bar_2", "figure")],
    [Input(melder_dropdown, "value"), Input("finance", "value"),
     Input("organisation", "value"), Input(wert_dropdown, "value"),
     Input("name", "value"), Input(jahr_dropdown, "value")],
)

def update_graph_1(melder, finance, organisation, wert, name, jahr):

  if (melder != "All") & (melder != []):
    dat_fil = df[df["Melder"].isin(melder)]
  else:
    dat_fil = df

  if finance == 0:
    dat_1 = dat_fil
  if finance == 1:
    dat_1 = dat_fil[dat_fil["ODA-Art"] == "Bil ODA"]
  if finance == 2:
    dat_1 = dat_fil[dat_fil["ODA-Art"] == "Multi ODA"]

  if (jahr != "All") & (jahr != []):
    dat_1 = dat_1[dat_1["Year"].isin(jahr)]

  datPie = dat_1.groupby(["Art der Organisation"])[[wert]].sum().reset_index()
  figPie = px.pie(datPie, values= wert, names='Art der Organisation')

  datMap = dat_1.groupby(["ISO", "Empfängerland"])[[wert]].sum().reset_index()
  figMap = px.choropleth(datMap, locations = "ISO", locationmode="ISO-3",
                        color_continuous_scale="Fall", color = wert, projection="natural earth")

  if (organisation != "All") & (organisation != []):
    datBar = dat_fil[dat_fil["Art der Organisation"].isin(organisation)]
  else:
    datBar = dat_fil

  if (name != "All") & (name != []):
    datBar = datBar[datBar["Organisation"].isin(name)]

  datBar_1 = datBar.groupby(["Finanzierungsart", "Year"])[[wert]].sum().reset_index()
  figBar = px.bar(datBar_1, x= "Year", y = wert, color='Finanzierungsart', barmode="group")

  datBar_2 = datBar.groupby(["Annex2", "Year"])[[wert]].sum().reset_index()
  figBar_2 = px.bar(datBar_2, x= "Year", y = wert, color='Annex2', barmode="group")

  return figPie, figBar, figMap, figBar_2

if __name__ == '__main__':
    app.run_server(debug=True)
