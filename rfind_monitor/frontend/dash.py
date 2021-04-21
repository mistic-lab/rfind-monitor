from rfind_monitor.utils.hashing import name_to_hash
import dash_core_components as dcc
import dash_html_components as html
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import ServersideOutput, Trigger, Dash, Input, Output, State

import numpy as np
import h5py

from rfind_monitor.frontend.crunch import fetch_integration, reduce_integration
import rfind_monitor.const as const


h5f = h5py.File(const.SOURCE_H5,'r')

y_range = [20, 60]

start_spec = np.zeros((const.WATERFALL_HEIGHT, const.SPEC_WIDTH))
start_freqs = np.linspace(0, 2e9, const.SPEC_WIDTH)



app = Dash(
    __name__,
    requests_pathname_prefix=const.DASH_PREFIX,
    title='RFInd Monitor',
    update_title=None,
    prevent_initial_callbacks=True,
    assets_folder=const.ASSETS_DIR
)

def serve_layout():

    return html.Div(
        [
            # dcc.Store(id='userStore', storage_type='memory', data={'spec': start_spec, 'freqs': start_freqs, 'timestamp': 0.0}),#data={'session_id':session_id}),
            dcc.Store(id='userStore'),
            dcc.Interval(id='check_for_data', interval=const.UPDATE_STORE_RATE),
            dcc.Interval(id='update_gui', interval=const.UPDATE_GUI_RATE),
            dcc.Graph(id='spec', responsive=True, config=dict(displayModeBar=False), 
                figure={
                    'data': [
                        {
                            'type': 'scattergl',
                            'y': start_spec[0],
                            'x': start_freqs,
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
                            'ticksuffix': ' dB',
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
                        'x': start_freqs,
                        # 'y': start_times,
                        'z': start_spec,
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
                            'ticksuffix': ' dB',
                        },
                        'colorscale': 'Rainbow',
                        'zmin': y_range[0],
                        'zmax': y_range[1],
                        'hovertemplate': "Freq: %{x} <br />Time: %{y} <br />Power: %{z} dB<extra></extra>"
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
                            'showexponent': 'all',
                            'exponentformat': 'SI',
                            'ticksuffix': 'Hz',
                            'color': '#a3a7b0',
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

app.layout = serve_layout


@app.callback(
    ServersideOutput("userStore","data"),
    [Input("check_for_data","n_intervals")],
    [
        State("spec", "relayoutData"),
        State("userStore", "data")
    ],
    prevent_initial_call=True
)
def update_store(index, relayoutData, userStore):
    existing_store = userStore

    if existing_store==None:
        existing_store = {'spec': start_spec, 'freqs': start_freqs, 'timestamp': 0.0}

    if relayoutData and 'xaxis.range[0]' in relayoutData:
        f1 = int(relayoutData['xaxis.range[0]'])
        f2 = int(relayoutData['xaxis.range[1]'])
    else:
        f1=const.FULL_FREQS[0]
        f2=const.FULL_FREQS[-1]
    
    old_timestamp = existing_store['timestamp']
    
    newLine, freqs, timestamp = fetch_integration(index, h5f, f1, f2, const.SPEC_WIDTH)

    if timestamp == old_timestamp:
        raise PreventUpdate
    else:

        spec = np.roll(existing_store['spec'],-1,0)
        spec[-1] = newLine

        existing_store['spec'] = spec
        existing_store['freqs'] = freqs
        existing_store['timestamp'] = timestamp

        return existing_store




# @app.callback(
#     Output("userStore", "data"),
#     [Input("check_for_data", "n_intervals")], # output n_intervals, an int
#     [
#         State("spec", "relayoutData"),
#         State("userStore", "data")
#     ],
#     prevent_initial_call=True
# )
# def update_store(index, relayoutData, userStore):

#     if relayoutData and 'xaxis.range[0]' in relayoutData:
#         f1 = int(relayoutData['xaxis.range[0]'])
#         f2 = int(relayoutData['xaxis.range[1]'])
#     else:
#         f1=const.FULL_FREQS[0]
#         f2=const.FULL_FREQS[-1]
    
#     old_timestamp = int(userStore['timestamp'])
    
#     newLine, freqs, timestamp = fetch_integration(index, h5f, f1, f2, const.SPEC_WIDTH)

#     app.logger.info(f"Old timestamp: {int(old_timestamp)} : {type(old_timestamp)}")
#     app.logger.info(f"New timestamp: {int(timestamp)} : {type(timestamp)}")
#     app.logger.info(f"They're the same: {timestamp == old_timestamp}\n")

#     if timestamp == old_timestamp:
#         app.logger.info("Preventing updating")
#         raise PreventUpdate
#     else:

#         newSpec = userStore['spec']
#         newSpec.pop(0)
#         newSpec.append(newLine)

#         # userStore['spec'].pop(0)
#         # userStore['spec'].append(newLine)

#         # userStore['freqs'] = freqs

#         # userStore['timestamp'] = timestamp

#         return {'spec': newSpec, 'freqs': freqs, 'timestamp': timestamp}

















# app.clientside_callback(
#     ClientsideFunction(
#         namespace='clientside',
#         function_name='update_plots'
#     ),
#     [
#         Output("spec", "extendData"),
#         Output("waterfall", "extendData"),
#     ],
#     [
#         Input("update_gui", "n_intervals"), # output n_intervals, an int
#     ],
#     State("userStore", "data"),
#     prevent_initial_call=True
# )

@app.callback(
    [
        Output("spec", "extendData"),
        Output("waterfall", "extendData"),
    ],
    [
        Trigger("update_gui", "n_intervals"), # output n_intervals, an int
    ],
    State("userStore", "data"),
    prevent_initial_call=True
)
def update_plots(userStore):
    if userStore == None:
        raise PreventUpdate

    updatedSpec = [{'y': [userStore['spec'][const.WATERFALL_HEIGHT-1]], 'x': [userStore['freqs']]}, [0], const.SPEC_WIDTH]
    updatedWaterfall = [{'z': [userStore['spec']]}, [0], const.WATERFALL_HEIGHT]

    return [updatedSpec, updatedWaterfall]

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)


