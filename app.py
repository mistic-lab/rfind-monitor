import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output, State
import h5py
import numpy as np

from dataService import fetch_integration

waterfall_height = 200 # px
spec_width = 1000
simDataFile = h5py.File('data.h5','r')

spec = np.zeros((waterfall_height, spec_width))





app = dash.Dash(__name__)


app.layout = html.Div([
    html.Div([
        dcc.Input(id='refresh_rate_chooser', type='number', placeholder="1 second refresh rate", min=0.1, max=10, step=0.05),
        dcc.Interval(id='refresh_rate', interval=1000), # ms
    ], style={'height':'10vh'}),
    html.Div([
        # dcc.Graph(id='spec-waterfall', responsive=True, config=dict(displayModeBar=False),
        #     figure={
        #         'data': [
        #             {
        #                 'name': 'spec',
        #                 'type': 'line',
        #                 'xaxis': 'x1',
        #                 'yaxis': 'y1',
        #                 'y': spec[0],
                        
        #             },
        #             {
        #                 'name': 'waterfall',
        #                 'type': 'heatmap',
        #                 'xaxis': 'x1',
        #                 'yaxis': 'y2',
        #                 'z': spec,
        #                 # 'aspect': 'equal',
        #                 'colorbar': {
        #                     'len': 0.5,
        #                     'x': 0.95,
        #                     'y': 0.75,
        #                     'yanchor': 'top'
        #                 },
        #             },
        #         ],
        #         'layout': {
        #             'width': '100%',
        #             'height': '100%',
        #             'margin': {
        #                 't': 0,
        #                 'b': 0,
        #                 'r': 0,
        #                 'l': 0,
        #             },
        #             'xaxis1': {
        #                 'anchor': 'y1',
        #                 'domain': [0.0, 1.0],
        #             },
        #             'yaxis1':{
        #                 'range': [0,60],
        #                 'fixedrange': True,
        #                 'anchor': 'free',
        #                 'domain': [0.8, 1.0],
        #                 'position': 0.0,
        #             },
        #             'yaxis2': {
        #                 'fixedrange': True,
        #                 'anchor': 'x1',
        #                 'domain': [0.0, 0.75],
        #             },
        #         }
        #     },
        #     style={
        #         'height': '100%',
        #         'margin': 0
        #     }
        # ),
        dcc.Graph(id='spec', responsive=True, config=dict(displayModeBar=False), 
            figure={
                'data': [
                    {
                        'type': 'line',
                        'y': spec[0],
                    },
                ],
                'layout': {
                    'width': '100%',
                    'height': '100%',
                    'margin': {
                        't': 0,
                        'b': 0,
                        'r': 0,
                        'l': 0,
                    },
                    'yaxis': {
                        'range': [0,60],
                        'fixedRange': True,
                    }
                }
            },
            style={
                'height': '20vh',
                'margin': 0
            }
        ),
        dcc.Graph(id='waterfall', responsive=True, config=dict(displayModeBar=False, doubleClick='reset'), 
            figure={
                'data': [{
                    'type': 'heatmap',
                    'z': spec,
                    # 'aspect': 'equal',
                    'colorbar': {
                        'len': 0.5,
                        'x': 0.95,
                        'y': 0.95,
                        'yanchor': 'top'
                    },
                }],
                'layout': {
                    'width': '100%',
                    'height': '100%',
                    'margin': {
                        't': 0,
                        'b': 0,
                        'r':0,
                        'l':0,
                    },
                    'yaxis': {
                        'fixedrange': True,
                    }
                }
            }
        ),
        # dcc.Store(id='data-store', storage_type='memory', data={'img': spec}) # memory means every page refresh. We want 'session' (every time the tab closes)
    ], style={'height':'80vh'}),
],
style={
    'height':'100vh',
    # 'min-height': '100%',
    # 'box-sizing': 'border-box',
    # 'overflow-x': 'hidden',
    # 'overflow-y': 'hidden'
}
)


## Callbacks 

# When playback speed is changed with the GUI the Interval rate is changed
@app.callback(
    Output("refresh_rate", "interval"),
    [Input("refresh_rate_chooser", "value")],
    prevent_initial_call=True
)
def update_refresh_rate(rate):
    return rate*1000



# Whenever the Interval triggers this runs
@app.callback(
    [
        # Output("spec-waterfall", "extendData"),
        Output("spec", "extendData"),
        Output("waterfall", "extendData"),
        # Output("data-store", "data")
    ],
    [
        Input("refresh_rate", "n_intervals") # output n_intervals, an int
    ],
    [
        # State("data-store", "data"), # while I think this is the smartest avenue, a global var seems faster
        State("spec", "relayoutData")
    ],
    prevent_initial_call=True
)
def update_spec(index, relayoutData, spec=spec):

    if 'xaxis.range[0]' in relayoutData:
        index_start = int(relayoutData['xaxis.range[0]'])
        index_end = int(relayoutData['xaxis.range[1]'])
    else:
        index_start = 0
        index_end = -1
    newLine, freqs, t, fs, NFFT = fetch_integration(index,simDataFile, start=index_start, end=index_end, length=spec_width)

    spec[0:-1] = spec[1:]
    spec[-1] = newLine

    # updatedData = dict(y=[[newLine], [np.arange(waterfall_height)]], z=[[newLine], [spec]]), [0], len(newLine)
    # return updatedData

    updatedSpec = dict(y=[newLine]), [0], spec_width
    updatedWaterfall = dict(z=[spec]), [0], waterfall_height

    return updatedSpec, updatedWaterfall






app.run_server(debug=True)

simDataFile.close()