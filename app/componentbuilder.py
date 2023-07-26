import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State
import elementstyling
from datetime import date, timedelta
import math
import pandas as pd
import plotly.express as px

def build_graph_component(card_title, open_expand_button_id, close_expand_button_id, question_button_id, modal_body_id, modal_id, graph_div_id, question_modal_id, card_description = "", element_styling = None, animate = False):
    if animate:
        graph_comp = dbc.Spinner([html.Div(dcc.Graph(id=graph_div_id, style={"height": "100%"}), id = f"""{graph_div_id}_div""")], color="primary")
    else:
        graph_comp = dbc.Spinner([html.Div(id=graph_div_id)], color="primary")
    data_graph = dbc.Card([dbc.Row([dbc.Col(html.H4(card_title, className="card-title"), width = 6), 
            dbc.Col(html.Div([ dbc.Button(html.I(className="fas fa-question", style={'fontSize': '30px'}), id=question_button_id, n_clicks=0, style =  elementstyling.IMG_STYLING),
                              dbc.Button(html.I(className="fas fa-expand", style={'fontSize': '30px'}), id=open_expand_button_id, n_clicks=0, style = elementstyling.IMG_STYLING), 
                             ], style = {"float": "right"}), width = 6)]),
            dbc.Modal(
                [
                dbc.ModalHeader([html.H4(card_title, className="card-title"), 
                dbc.Button(html.I(className="fas fa-expand", style={'fontSize': '30px'}), id=close_expand_button_id, n_clicks=0, style = {"backgroundColor": "transparent"})], close_button=False),
                dbc.ModalBody(id = modal_body_id),
                ],
            id=modal_id,
            is_open=False,
            fullscreen=True,
            keyboard=False,
            backdrop="static",
            ),
            dbc.Modal(
                [
                dbc.ModalHeader([html.H4("Description", className="card-title")]),
                dbc.ModalBody(html.H5(card_description))
                ],
                id=question_modal_id,
                is_open=False,
                size="xl",
                keyboard=False,
                backdrop="static",
            ),
        graph_comp],  body=True, style=element_styling)
    return data_graph

def build_graph_component_noq(card_title_id, open_expand_button_id, close_expand_button_id, modal_body_id, modal_id, graph_div_id, full_card_id, element_styling = None):
    data_graph = dbc.Card([dbc.Row([dbc.Col(html.H4(id = card_title_id, className="card-title"), width = 6), 
            dbc.Col(html.Div([dbc.Button(html.I(className="fas fa-expand", style={'fontSize': '30px'}), id=open_expand_button_id, n_clicks=0, style = elementstyling.IMG_STYLING), 
                             ], style = {"float": "right"}), width = 6)]),
            dbc.Modal(
                [
                dbc.ModalHeader([html.H6(className="card-title"), 
                dbc.Button(html.I(className="fas fa-expand", style={'fontSize': '30px'}), id=close_expand_button_id, n_clicks=0, style = {"backgroundColor": "transparent"})], close_button=False),
                dbc.ModalBody(id = modal_body_id),
                ],
                id=modal_id,
                is_open=False,
                fullscreen=True,
                keyboard=False,
                backdrop="static",
            ),
        html.Div(id=graph_div_id)],  id = full_card_id, body=True, style=element_styling)
    return data_graph


def build_form_component(card_title, dropdowns, dateranges, submitid, question_button_id, question_modal_id, card_description = "", element_styling = None, card_coords = None,):
    modal_body = html.H5([card_description, html.Br(), html.Br(), "Station Locations:", get_map_component(card_coords)]) if card_coords else \
        html.H5([card_description, html.Br(), html.Br()])
    form = []
    for drop in dropdowns:
        desc, options, id = drop[0], drop[1], drop[2]
        curr_dropdown = html.Div(
            [
                dbc.Label(desc),
                dcc.Dropdown(
                    options,
                    options[0],
                    id=id,
                    clearable=False,
                ),
            ],
        )
        form.append(curr_dropdown)
        form.append(html.Br())
    for dater in dateranges:
        desc, id = dater[0], dater[1]
        daterange = html.Div(
            [   dbc.Row([dbc.Label(desc)]),    
                dcc.DatePickerRange(
                id=id,
                min_date_allowed=date(1900, 1, 1),
                max_date_allowed=date.today(),
                start_date=date.today() - timedelta(10),
                end_date=date.today()
            )
            ],
        )
        form.append(daterange)
        form.append(html.Br())
    form.append(dbc.Button("Submit", color="primary",
                                            className="mb-3", id = submitid))
    return dbc.Card([dbc.Row([dbc.Col(html.H4(card_title, className="card-title"), width = 9), 
            dbc.Col(html.Div([ dbc.Button(html.I(className="fas fa-question", style={'fontSize': '30px'}), id=question_button_id, n_clicks=0, style =  elementstyling.IMG_STYLING),
                             ], style = {"float": "right"}), width = 3)]), 
                dbc.Modal(
                [
                dbc.ModalHeader([html.H4("Description", className="card-title")]),
                dbc.ModalBody(modal_body)
                ],
                id=question_modal_id,
                is_open=False,
                size="xl",
                keyboard=False,
                backdrop="static",
            ), dbc.Form(form)], body=True, style = element_styling)


def get_map_component(coords):
    if not coords: 
        return None
    
    ## convert string to int
    for tup in coords:
        tup[1] = float(tup[1])
        tup[2] = float(tup[2])
    df = pd.DataFrame(coords, columns=['Station', 'Latitude', 'Longitude'])

    fig = px.scatter_mapbox(df, lat="Latitude", lon="Longitude", color = "Station", zoom=3, height=245)
    fig.update_layout(
        mapbox_style="white-bg",
        mapbox_layers=[
            {
                "below": 'traces',
                "sourcetype": "raster",
                "sourceattribution": "United States Geological Survey",
                "source": [
                    "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"
                ]
            }
        ])
    fig.update_traces(marker=dict(
        size = 20
    ),)
    fig.update_layout(
    margin=dict(l=5,r=5,b=5,t=20),
    )
    fig.update_layout(template='plotly_dark')
    return dcc.Graph(figure = fig)

