import streamsync as ss

initial_state = ss.init_state({
    "value": "",
})

def update_value(state, payload):
    state['value'] = payload

def execute_test(state, ui):
    exec(state['code'])


with ss.init_ui() as ui:
    with ui.find('initialization'):
        ui.Text({"text": "Initialization successful!"});
