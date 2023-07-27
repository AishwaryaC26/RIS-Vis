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
coords = ast.literal_eval(os.environ["SEISMIC_COORDS"])

#create list of stations from "stations" dict
stationsoptions = list(stations.keys())

form_desc = "The Seismic Data Visualization form can be used to visualize waveforms, spectrograms, and power spectral densities of various seismic stations." \
    +" Choose to filter the waveform by displacement, velocity, or acceleration."

waveform_desc = "This waveform graph displays seismogram data after being filtered by displacement, velocity, or acceleration."

spectrogram_desc = "Spectrograms are created from their corresponding waveform data. Amplitude is represented by color, \
    where lighter colors represent a higher amplitude."

psd_desc = "The power spectral density graph represents the relative amplitudes of frequencies represented within a time range \
    (chosen in the form)."

# method to get all components for seismic page
def get_all_seismic_elements():
    filter_options = ['DISP', 'VEL', 'ACC']
    seismic_form = componentbuilder.build_form_component("Seismic Data Visualization Form", [("Select seismic station:", stationsoptions, "dropdownseismic"), 
                    ("Filter waveform by:", filter_options, "dropdownwavefilt")], [("Select date range:", 'timeframepicker'),], "formsubmitbut", "open-seismicq-button", "seismicq-modal", form_desc, elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP, coords, )
    waveform_data_graph = componentbuilder.build_graph_component("Waveform Data", "open-waveform-button", "close-waveform-button", "open-waveformq-button", "open-waveform-modal-body", "open-waveform-modal", "waveformgraph", "waveformq-modal", waveform_desc, elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    seismic_row_one = dbc.Row([dbc.Col([seismic_form], width = 4), dbc.Col([waveform_data_graph], width = 8, )])
    spectrogram_graph = componentbuilder.build_graph_component("Spectrogram", "open-spec-button", "close-spec-button", "open-specq-button", "open-spec-modal-body", "open-spec-modal", "spectrogramgraph", "specq-modal", spectrogram_desc, elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)
    psd_graph = componentbuilder.build_graph_component("Power Spectral Density", "open-psd-button", "close-psd-button", "open-psdq-button", "open-psd-modal-body", "open-psd-modal", "psdgraph", "psdq-modal", psd_desc, elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP)
    seismic_row_two = dbc.Row([dbc.Col([spectrogram_graph], width =7,), dbc.Col([psd_graph],  width =5)])
    ALL_SEISMIC_ELEMENTS = [seismic_row_one, seismic_row_two]
    return ALL_SEISMIC_ELEMENTS