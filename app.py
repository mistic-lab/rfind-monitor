import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output
import h5py
import numpy as np

simDataFile = h5py.File('data.h5','r')
spec = simDataFile['spec']

waterfall_height = 200 # px


app = dash.Dash(__name__)


app.layout = html.Div([
    html.Div([
        dcc.Input(id='refresh_rate_chooser', type='number', placeholder="1 second refresh rate", min=0.5, max=10, step=0.1),
        dcc.Interval(id='refresh_rate', interval=1000), # ms
    ]),
    html.Div([
        dcc.Graph(id='spec', responsive=True, config=dict(displayModeBar=False),
            figure={
                'data': [{
                    'type': 'line',
                    'y': spec[0],
                    
                }],
                'layout': {
                    'width': '100%',
                    'height': '100%',
                    'margin': {
                        't': 0,
                        'b':0,
                        'r':0,
                        'l':0,
                    },
                    'yaxis': {
                        'range': [0,60]
                    },
                }
            },
            style={'height': '20vh'}
        ),
        dcc.Graph(id='waterfall', responsive=True, config=dict(displayModeBar=False, doubleClick='reset'), 
            figure={
                'data': [{
                    'type': 'heatmap',
                    'z': spec[0:waterfall_height],
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
                        'fixedrange': True
                    }
                }
            }
        )
    ]),
],
style={'height':'100vh'}
)


## Callbacks 
@app.callback(
    Output("refresh_rate", "interval"),
    [Input("refresh_rate_chooser", "value")], prevent_initial_call=True)
def update_refresh_rate(rate):
    return rate*1000

@app.callback([
    Output("spec", "extendData"),
    Output("waterfall", "extendData")
], [Input("refresh_rate", "n_intervals")], prevent_initial_call=True)
def update_spec(index):
    newSpec = spec[index:index+waterfall_height]
    newLine = spec[index]
    updatedSpec = dict(y=[newLine]), [0], spec.shape[1]
    updatedWaterfall = dict(z=[newSpec]),[0], waterfall_height

    #TODO This would be better since it would not need a full new matrix each time
    # newSpec = spec[index] 
    # updatedSpec = dict(y=[newSpec]), [0], spec.shape[1]
    # updatedWaterfall = dict(z=[newSpec]),[0], waterfall_height

    return updatedSpec, updatedWaterfall

#TODO use relayoutData from zoom event on waterfall to update xaxis on spec
#TODO https://dash.plotly.com/interactive-graphing
# @app.callback(
#     Output("spec","relayoutData"),
#     [Input("waterfall","relayoutData")], prevent_initial_call=True)
# def update_spec_xaxis(relayOutData):






app.run_server(debug=True)

simDataFile.close()