import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import numpy as np
import zmq

from dataService import fetch_integration, pull_integration
from api import NBINS, SPEC_WIDTH, WATERFALL_HEIGHT, FULL_FREQS


context = zmq.Context()
consumer_receiver = context.socket(zmq.PULL)
consumer_receiver.bind("tcp://127.0.0.1:5569")
poller = zmq.Poller()
poller.register(consumer_receiver, zmq.POLLIN)

y_range = [20, 60]

spec = np.zeros((WATERFALL_HEIGHT, SPEC_WIDTH))
current_freqs = np.linspace(0, 2e9, SPEC_WIDTH)





app = dash.Dash(__name__, requests_pathname_prefix='/live/', title='RFInd Monitor', update_title=None)
# app = dash.Dash(__name__, title='RFInd Monitor', update_title=None)

app.layout = html.Div(
    [
        dcc.Interval(id='check_for_data', interval=500), # ms
        dcc.Graph(id='spec', responsive=True, config=dict(displayModeBar=False), 
            figure={
                'data': [
                    {
                        'type': 'scattergl',
                        'y': spec[0],
                        'x': current_freqs,
                        'line': {
                            'color': 'white',
                            'width': 2,
                        },
                        'fill': 'tozeroy',
                    },
                ],
                'layout': {
                    'width': '100%',
                    'height': '100%',
                    'margin': {
                        't': 10,
                        'b': 40,
                        'r': 0,
                        'l': 0,
                    },
                    'yaxis': {
                        'range': y_range,
                        'fixedRange': True,
                        # 'title': 'dB',
                        'ticklabelposition': 'inside',
                        'showticklabels': False,
                        'color': '#a3a7b0',

                    },
                    'xaxis': {
                        'showexponent': 'all',
                        'exponentformat': 'SI',
                        'ticksuffix': 'Hz',
                        'color': '#a3a7b0',

                    },
                    'plot_bgcolor': '#23272c',
                    'paper_bgcolor': '#23272c',
                }
            },
            style={
                'height': '20%',
                'margin': 0
            }
        ),
        dcc.Graph(id='waterfall', responsive=True, config=dict(displayModeBar=False, doubleClick='reset'), 
            figure={
                'data': [{
                    'type': 'heatmap',
                    'z': spec,
                    'x': current_freqs,
                    'colorbar': {
                        'len': 0.5,
                        'x': 0.98,
                        'y': 0.98,
                        'yanchor': 'top',
                        'xanchor': 'right',
                        'bgcolor': '#23272c',
                        'tickfont': {
                            'color': 'white',
                        },
                    },
                    'colorscale': 'Rainbow',
                    'zmin': y_range[0],
                    'zmax': y_range[1],
                }],
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
                        'fixedrange': True,
                        'showticklabels': False,
                        'showgrid': False,
                        'color': '#a3a7b0',
                        'ticks': '',
                    },
                    'xaxis': {
                        'fixedrange': True,
                        'color': '#a3a7b0',
                        'ticks': '',
                    },
                    'plot_bgcolor': '#23272c',
                    'paper_bgcolor': '#23272c',
                }
            },
            style={'height': '80%', 'margin': 0}
        ),
    ], style={
        'height':'100vh',
        'margin':0,
    }
)


# Whenever the Interval triggers this runs
@app.callback(
    [
        Output("spec", "extendData"),
        Output("waterfall", "extendData"),
    ],
    [
        Input("check_for_data", "n_intervals") # output n_intervals, an int
    ],
    [
        State("spec", "relayoutData")
    ],
    prevent_initial_call=True
)
def update_spec(index, relayoutData, spec=spec, current_freqs=current_freqs, poller=poller, receiver=consumer_receiver): #TODO globalvars are lame

    socks = dict(poller.poll(1))
    if not socks:
        raise PreventUpdate
    else:
        if relayoutData and 'xaxis.range[0]' in relayoutData:# and 'xaxis.range[1]' in relayoutData:
            f1 = int(relayoutData['xaxis.range[0]'])
            f2 = int(relayoutData['xaxis.range[1]'])
        else:
            f1 = current_freqs[0]
            f2 = current_freqs[-1]
    
    newLine, freqs = pull_integration(receiver, f1, f2, SPEC_WIDTH)
    # newLine, freqs = fetch_integration(index, simDataFile, f1=f1, f2=f2, length=spec_width)

    spec[0:-1] = spec[1:]
    spec[-1] = newLine

    updatedSpec = dict(y=[newLine], x=[freqs]), [0], SPEC_WIDTH
    updatedWaterfall = dict(z=[spec]), [0], WATERFALL_HEIGHT


    return updatedSpec, updatedWaterfall



server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)


