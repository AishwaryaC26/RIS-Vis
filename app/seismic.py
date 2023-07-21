import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State
import elementstyling
from datetime import date
import os, ast
from dotenv import load_dotenv
import componentbuilder


load_dotenv()
stations = ast.literal_eval(os.environ["SEISMIC_STATIONS"])

#create list of stations from "stations" dict
stationsoptions = list(stations.keys())


def get_all_seismic_elements():
    filter_options = ['DISP', 'VEL', 'ACC']
    seismic_form = componentbuilder.build_form_component("Seismic Data Visualization Form", [("Select seismic station:", stationsoptions, "dropdownseismic"), 
                    ("Filter waveform by:", filter_options, "dropdownwavefilt")], [("Select date range:", 'timeframepicker'),], "formsubmitbut", "open-seismicq-button", "seismicq-modal", "",elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    waveform_data_graph = componentbuilder.build_graph_component("Waveform Data", "open-waveform-button", "close-waveform-button", "open-waveformq-button", "open-waveform-modal-body", "open-waveform-modal", "waveformgraph", "waveformq-modal", "", elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    seismic_row_one = dbc.Row([dbc.Col([seismic_form], width = 4), dbc.Col([waveform_data_graph], width = 8, )])
    spectrogram_graph = componentbuilder.build_graph_component("Spectrogram", "open-spec-button", "close-spec-button", "open-specq-button", "open-spec-modal-body", "open-spec-modal", "spectrogramgraph", "specq-modal", "", elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    psd_graph = componentbuilder.build_graph_component("Power Spectral Density", "open-psd-button", "close-psd-button", "open-psdq-button", "open-psd-modal-body", "open-psd-modal", "psdgraph", "psdq-modal", "", elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    seismic_row_two = dbc.Row([dbc.Col([spectrogram_graph], width =7,), dbc.Col([psd_graph],  width =5)])
    ALL_SEISMIC_ELEMENTS = [seismic_row_one, seismic_row_two]
    return ALL_SEISMIC_ELEMENTS