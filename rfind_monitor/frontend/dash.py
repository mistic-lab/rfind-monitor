from rfind_monitor.utils.hashing import name_to_hash
import dash
import dash_core_components as dcc
import dash_html_components as html
# from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import ServersideOutput, Trigger, Dash, Input, Output, State

import numpy as np
import datetime
from dateutil import tz
import h5py
# from brain_plasma import Brain
# import pyarrow.plasma as plasma
import uuid

from rfind_monitor.frontend.crunch import fetch_integration, reduce_integration
import rfind_monitor.const as const


h5f = h5py.File(const.SOURCE_H5,'r')
# brain = Brain(path=const.PLASMA_SOCKET)
# brain = plasma.connect(const.PLASMA_SOCKET)

y_range = [20, 60]

start_spec = np.zeros((const.WATERFALL_HEIGHT, const.SPEC_WIDTH))
start_freqs = np.linspace(0, 2e9, const.SPEC_WIDTH)

# start_times = datetime.datetime.now(tz=tz.tzstr('America/Vancouver')) - np.arange(const.WATERFALL_HEIGHT) * datetime.timedelta(seconds=1)
# start_timestamps=[int(t.timestamp()) for t in start_times[::-1]]
# del start_times




app = Dash(__name__, requests_pathname_prefix=const.DASH_PREFIX, title='RFInd Monitor', update_title=None)

def serve_layout():
    # session_id = str(uuid.uuid4())

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

#     session_id = userStore['session_id']
#     # app.logger.info(f"In callback: {session_id}")
#     # timestamp_id = name_to_hash('timestamp')


#     if ('timestamp' not in brain):
#     # app.logger.info(brain.contains(timestamp_id))
#     # if not brain.contains(timestamp_id):
#         raise PreventUpdate

#     # user_timestamp_id = name_to_hash('timestamp'+session_id)
#     # user_spec_id = name_to_hash('spec'+session_id)
#     # user_freqs_id = name_to_hash('freqs'+session_id)
#     if ('timestamp'+session_id not in brain):
#     # if not brain.contains(user_timestamp_id):
#         # user_spec_id = brain.put(start_spec)
#         # user_freqs_id = brain.put(start_freqs)
#         # user_timestamp_id = brain.put(0.0)

#         brain['spec'+session_id] = start_spec
#         brain['freqs'+session_id] = start_freqs
#         brain['timestamp'+session_id] = 0.0

#     if (brain['timestamp'] == brain['timestamp'+session_id]):
#     # if (brain.get(user_timestamp_id) == brain.get(timestamp_id)):
#         raise PreventUpdate

#     # app.logger.info(f"Shared timestamp: {brain['timestamp']}")
#     # app.logger.info(f"User timestamp: {brain['timestamp'+session_id]}\n")

#     latest_integration = np.array(brain['spec'])
#     # spec_id = name_to_hash('spec')
#     # latest_integration = np.array(brain.get(spec_id))

#     if relayoutData and 'xaxis.range[0]' in relayoutData:
#         f1 = int(relayoutData['xaxis.range[0]'])
#         f2 = int(relayoutData['xaxis.range[1]'])
#     else:
#         f1=const.FULL_FREQS[0]
#         f2=const.FULL_FREQS[-1]

#     reduced_integration, new_freqs = reduce_integration(latest_integration, f1, f2, const.SPEC_WIDTH)



#     # userStore['spec'].pop(0)
#     # userStore['spec'].append(reduced_integration)
#     # userStore['freqs'] = new_freqs
#     # userStore['timestamp'] = brain['timestamp']

#     spec = np.roll(brain['spec'+session_id],-1,0)
#     spec[-1] = reduced_integration
#     brain['spec'+session_id] = spec
#     brain['freqs'+session_id] = new_freqs
#     brain['timestamp'+session_id] = brain['timestamp']

#     # spec = np.roll(brain.get(user_spec_id),-1,0)
#     # spec[-1] = reduced_integration
#     # user_spec_id = brain.put(spec)
#     # user_freq_id = brain.put(new_freqs)
#     # user_timestamp_id = brain.put(brain.get(timestamp_id))

#     return userStore

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

    # app.logger.info(f"Old timestamp: {int(old_timestamp)}")
    # app.logger.info(f"New timestamp: {int(timestamp)}")

    if timestamp == old_timestamp:
        app.logger.info("Preventing updating")
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

# app.clientside_callback(
#     """
#     function (index, storeData) {
#         if (index !== undefined) {
#             console.log("Updating plot from timestamp "+storeData.timestamp)
#             const updatedSpec = [{y: [storeData.spec[storeData.spec.length-1]], x: [storeData.freqs]}, [0], storeData.freqs.length]
#             const updatedWaterfall = [{z: [storeData.spec]}, [0], storeData.spec.length]
#             return [updatedSpec, updatedWaterfall];
#         } else {
#             throw window.dash_clientside.PreventUpdate;
#         }
#     }
#     """,
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
        Input("update_gui", "n_intervals"), # output n_intervals, an int
    ],
    State("userStore", "data"),
    prevent_initial_call=True
)
def update_plots(index, userStore):
    # session_id = userStore['session_id']

    updatedSpec = [{'y': [userStore['spec'][const.WATERFALL_HEIGHT-1]], 'x': [userStore['freqs']]}, [0], const.SPEC_WIDTH]
    updatedWaterfall = [{'z': [userStore['spec']]}, [0], const.WATERFALL_HEIGHT]

    # updatedSpec = [{'y': [brain['spec'+session_id][const.WATERFALL_HEIGHT-1]], 'x': [brain['freqs'+session_id]]}, [0], const.SPEC_WIDTH]
    # updatedWaterfall = [{'z': [brain['spec'+session_id]]}, [0], const.WATERFALL_HEIGHT]
    
    # user_spec_id = name_to_hash('spec'+session_id)
    # user_freqs_id = name_to_hash('freqs'+session_id)

    # updatedSpec = [{'y': [brain.get(user_spec_id)[const.WATERFALL_HEIGHT-1]], 'x': [brain.get(user_freqs_id)]}, [0], const.SPEC_WIDTH]
    # updatedWaterfall = [{'z': [brain.get(user_spec_id)]}, [0], const.WATERFALL_HEIGHT]

    return [updatedSpec, updatedWaterfall]

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)


