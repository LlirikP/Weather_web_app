import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
from main import get_weather, get_weather_data, get_coordinates_from_city

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Weather Data Visualization", style={'textAlign': 'center'}),

    html.Div([
        html.Label("Enter City Name:"),
        dcc.Input(id='city-input', type='text', placeholder='City Name', style={'marginRight': '10px'}),
        html.Button('Submit', id='submit-button', n_clicks=0),
    ], style={'marginBottom': '20px'}),

    html.Div([
        html.Label("Select Weather Parameter:"),
        dcc.Dropdown(
            id='weather-parameter',
            options=[
                {'label': 'Temperature', 'value': 'temperature'},
                {'label': 'Wind Speed', 'value': 'wind'},
                {'label': 'Precipitation Probabilities', 'value': 'precipitation'}
            ],
            value='temperature',
            clearable=False
        )
    ], style={'marginBottom': '20px'}),

    dcc.Graph(id='weather-graph'),
])


@app.callback(
    Output('weather-graph', 'figure'),
    [Input('submit-button', 'n_clicks'),
     Input('weather-parameter', 'value')],
    [State('city-input', 'value')]
)
def update_graph(n_clicks, parameter, city_name):
    if n_clicks == 0 or not city_name:
        return go.Figure()

    latitude, longitude, location_key = get_coordinates_from_city(city_name)
    weather_data = get_weather_data(get_weather(latitude, longitude))

    if not weather_data:
        raise ValueError("Weather data is missing.")

    if parameter == 'precipitation':
        rain_probability = weather_data.get('rain probability', 0)
        snow_probability = weather_data.get('snow probability', 0)

        x = ['Rain Probability', 'Snow Probability']
        y = [rain_probability, snow_probability]
        figure = go.Figure(
            data=go.Bar(
                x=x,
                y=y,
                marker=dict(
                    color=['#1f77b4', '#aec7e8'],
                    line=dict(color='black', width=1.5)
                ),
                text=y,
                textfont=dict(size=16, color='black'),
                textposition='auto'
            ),
            layout=go.Layout(
                title=f'Precipitation Probabilities in {city_name}',
                xaxis=dict(
                    title='Precipitation Type',
                    titlefont=dict(size=18, color='#7f7f7f'),
                    tickfont=dict(size=14)
                ),
                yaxis=dict(
                    title='Probability (%)',
                    titlefont=dict(size=18, color='#7f7f7f'),
                    tickfont=dict(size=14)
                ),
                template='plotly_white',
                titlefont=dict(size=22),
                margin=dict(l=40, r=40, t=40, b=40)
            )
        )
        return figure

    elif parameter == 'temperature':
        min_temp = weather_data.get('min temperature', None)
        max_temp = weather_data.get('max temperature', None)

        x = ['Min Temperature', 'Max Temperature']
        y = [min_temp, max_temp]
        figure = go.Figure(
            data=go.Scatter(
                x=x,
                y=y,
                mode='lines+markers',
                line=dict(color='#ff7f0e', width=3),
                marker=dict(size=10, color='rgb(255,127,14)', symbol='circle')
            ),
            layout=go.Layout(
                title=f'Temperature in {city_name}',
                xaxis=dict(
                    title='Temperature difference',
                    titlefont=dict(size=18, color='#7f7f7f'),
                    tickfont=dict(size=14)
                ),
                yaxis=dict(
                    title='Degrees (°C)',
                    titlefont=dict(size=18, color='#7f7f7f'),
                    tickfont=dict(size=14)
                ),
                template='plotly_white',
                titlefont=dict(size=22),
                margin=dict(l=40, r=40, t=40, b=40)
            )
        )
        return figure

    elif parameter == 'wind':
        wind_speed = weather_data.get('wind speed', None)

        labels = ['Wind Speed']
        values = [wind_speed]
        figure = go.Figure(
            data=go.Bar(
                x=labels,
                y=values,
                marker=dict(color='#2ca02c')
            ),
            layout=go.Layout(
                title=f'Wind Speed in {city_name}',
                titlefont=dict(size=22),
                xaxis=dict(title="Wind Speed"),
                yaxis=dict(title="Speed (km/h)"),
                template='plotly_white',
                margin=dict(l=40, r=40, t=40, b=40)
            )
        )
        return figure

    else:
        raise ValueError(f"Invalid parameter selected: {parameter}")


if __name__ == '__main__':
    app.run_server(debug=True)
