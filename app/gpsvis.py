import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html, State
import elementstyling
from datetime import date, timedelta 
import ast, os
from dotenv import load_dotenv
import componentbuilder


# GPS Visualization Page Elements
load_dotenv()

gps_stations = ast.literal_eval(os.environ["GPS_STATIONS"])
coords = ast.literal_eval(os.environ["GPS_STATION_COORDS"])

tracks_form_desc = "Use the GPS Tracks form to visualize tracks of the movements of GPS stations within a specific time range."

tracks_desc = "This graph shows the movement of GPS stations over time. Click on a station's marker to zoom in to only its movements."

baseline_form_desc = "Use this form to visualize the baseline length/angle movements of GPS stations with respect to a specific reference \
    station"

rel_mov = "This graph displays relative positions of stations with respect to the reference station over time."

length_desc = "This graph displays the distance between stations from the reference station over time."

angle_desc = "This graph displays the bearing between stations from the reference station over time."

length_res_desc = "This graph displays the distance residual between stations from the reference station over time."

angle_res_desc = "This graph displays the bearing residual between stations from the reference station over time."


def get_all_gpsvis_elements():
    gps_form = componentbuilder.build_form_component("GPS Tracks Form", [], [("Select date range:", 'gps_vis_datepicker'),], "gpsvis_formsubmitbut", "open-gpsvis1q-button", "gpsvis1-q-modal", tracks_form_desc, elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP, coords)

    gps_animation = componentbuilder.build_graph_component("Tracks of GPS Stations", "open-gpsvis-ani-modal", 
                                                            "close-gpsvis-ani-modal", "open-gpsvis-ani-q-button", "gpsvis-ani-modal-body", "gpsvis-ani-modal", "gps_animation", "gpsvis-ani-q-modal", tracks_desc, elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP, True)
    
    gps_row_one = dbc.Row([dbc.Col([gps_form], width = 4), dbc.Col([gps_animation], width = 8)])
    
    gps_form2 = componentbuilder.build_form_component("Deformation Visualization Form", [("Select Reference GPS station:", gps_stations, "gps_vis_dropdown2")], [("Select date range:", "gps_vis_datepicker2")], "gpsvis_formsubmitbut2", "open-gpsvis2q-button", "gpsvis2-q-modal", baseline_form_desc, elementstyling.CARD_HALF_WIDTH_LEFT_DOWNUP)

    gps_animation2 = componentbuilder.build_graph_component("Relative Movement over Time", "open-gpsvis-ani2-modal", 
                                                            "close-gpsvis-ani2-modal", "open-gpsvis-ani2-q-button", "gpsvis-ani2-modal-body", "gpsvis-ani2-modal", "gps_animation2", "gpsvis-ani2-q-modal", rel_mov, elementstyling.CARD_HALF_WIDTH_RIGHT_DOWNUP,)

    gps_row_two = dbc.Row([dbc.Col(gps_form2, width = 4), dbc.Col([gps_animation2,], width = 8)])

    baseline_length = componentbuilder.build_graph_component("Baseline Length Graph", "open-gpsvis-base-modal", 
                                                            "close-gpsvis-base-modal", "open-gpsvis-base-q-button", "gpsvis-base-modal-body", "gpsvis-base-modal", "baseline_length", "gpsvis-base-q-modal", length_desc, elementstyling.CARD_HALF_WIDTH_LEFT)

    baseline_orientation = componentbuilder.build_graph_component("Baseline Orientation Graph", "open-gpsvis-orient-modal", 
                                                            "close-gpsvis-orient-modal", "open-gpsvis-orient-q-button", "gpsvis-orient-modal-body", "gpsvis-orient-modal", "baseline_orient", "gpsvis-orient-q-modal", angle_desc, elementstyling.CARD_HALF_WIDTH_RIGHT)

    baseline_first_row = dbc.Row([dbc.Col(baseline_length, width = 6), dbc.Col(baseline_orientation, width = 6)])

    baseline_length_residual = componentbuilder.build_graph_component("Baseline Length Residual Graph", "open-gpsvis-lengthres-modal", 
                                                            "close-gpsvis-lengthres-modal", "open-gpsvis-lengthres-q-button", "gpsvis-lengthres-modal-body", "gpsvis-lengthres-modal", "baseline_length_resid", "gpsvis-lengthres-q-modal", length_res_desc, elementstyling.CARD_HALF_WIDTH_LEFT_DOWN)

    baseline_orientation_residual = componentbuilder.build_graph_component("Baseline Orientation Residual Graph", "open-gpsvis-orientres-modal",  
                                                            "close-gpsvis-orientres-modal", "open-gpsvis-orientres-q-button", "gpsvis-orientres-modal-body", "gpsvis-orientres-modal", "baseline_orient_resid", "gpsvis-orientres-q-modal", angle_res_desc, elementstyling.CARD_HALF_WIDTH_RIGHT_DOWN)
    
    baseline_second_row = dbc.Row([dbc.Col(baseline_length_residual, width = 6), dbc.Col(baseline_orientation_residual, width = 6), html.Br(), html.Br()])

    return [gps_row_one, gps_row_two, baseline_first_row, html.Br(), baseline_second_row]