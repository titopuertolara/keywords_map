import dash
from dash import dcc, html, callback, Output, Input, State
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div([
    dcc.Dropdown(
        id='tag-input',
        options=[],
        value=[],
        multi=True,
        placeholder='Add a keyword...'
    ),
    dcc.Input(
        id='new-tag-input',
        type='text',
        placeholder='Enter a new tag',
        style={'margin-top': '10px'}
    ),
    dbc.Button('Add Tag', id='add-tag-button', n_clicks=0, style={'margin-top': '10px'}),
    html.Div(id='output', style={'margin-top': '20px'})
])

@app.callback(
    Output('tag-input', 'options'),
    Output('tag-input', 'value'),
    Input('add-tag-button', 'n_clicks'),
    State('new-tag-input', 'value'),
    State('tag-input', 'options'),
    State('tag-input', 'value')
)
def add_tag(n_clicks, new_tag, current_options, current_value):
    if n_clicks > 0 and new_tag:
        new_option = {'label': new_tag, 'value': new_tag}
        if new_option not in current_options:
            current_options.append(new_option)
            current_value.append(new_tag)
    return current_options, current_value

@app.callback(
    Output('output', 'children'),
    Input('tag-input', 'value')
)
def update_output(tags):
    return 'You have entered: {}'.format(', '.join(tags))

if __name__ == '__main__':
    app.run_server(debug=True)
