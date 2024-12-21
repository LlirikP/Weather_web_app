import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
from main import get_weather, get_weather_data, get_coordinates_from_city

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Weather Route Visualization", style={'textAlign': 'center'}),
    html.Div([
        html.Label("Enter city names"),
        dcc.Textarea(
            id='city-input',
            placeholder='City 1, City 2, City 3...',
            style={'width': '100%', 'height': '100px'}
        ),
        html.Button('Submit', id='submit-button', n_clicks=0),
    ], style={'marginBottom': '20px'}),
    html.Div([
        html.Label("Select Forecast Days:"),
        dcc.RadioItems(
            id='forecast-days',
            options=[
                {'label': '1 Hour', 'value': 0},
                {'label': '1 Day', 'value': 1},
                {'label': '5 Days', 'value': 5},
            ],
            value=1,
            inline=True
        )
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

    html.Div([
        html.H3("Weather Route Map"),
        dcc.Graph(id='route-map')
    ], style={'marginTop': '20px'})
])


@app.callback(
    [Output('weather-graph', 'figure'),
     Output('route-map', 'figure')],
    [Input('submit-button', 'n_clicks'),
     Input('weather-parameter', 'value'),
     Input('forecast-days', 'value')],
    [State('city-input', 'value')]
)
def update_graph(n_clicks, parameter, forecast_days, city_input):
    map_figure = go.Figure()
    if n_clicks == 0 or not city_input:
        return go.Figure()

    city_names = [city.strip() for city in city_input.split(',')]
    all_weather_data = []
    map_data = []

    for city_name in city_names:
        latitude, longitude, location_key = get_coordinates_from_city(city_name)
        if not location_key:
            raise ValueError(f"City {city_name} not found.")

        weather_data = get_weather(latitude, longitude, location_key, forecast_days)
        if not weather_data:
            raise ValueError(f"Could not retrieve weather for {city_name}.")
        if forecast_days != 0:
            for i in range(forecast_days):
                daily_data = get_weather_data(weather_data, i)
                daily_data["City"] = city_name
                daily_data["Day"] = f"Day {i + 1}"
                all_weather_data.append(daily_data)
        else:
            daily_data = get_weather_data(weather_data, 0)
            daily_data["City"] = city_name
            daily_data["Day"] = f"Hour 1"
            all_weather_data.append(daily_data)

        map_data.append({
            "lat": latitude,
            "lon": longitude,
            "city": city_name
        })

    if parameter == 'precipitation':
        x = [f"{data['City']} ({data['Day']})" for data in all_weather_data]
        rain_probs = [data['rain probability'] for data in all_weather_data]
        snow_probs = [data['snow probability'] for data in all_weather_data]

        figure = go.Figure(
            data=[
                go.Bar(name="Rain Probability", x=x, y=rain_probs, marker_color='#1f77b4'),
                go.Bar(name="Snow Probability", x=x, y=snow_probs, marker_color='#aec7e8')
            ],
            layout=go.Layout(
                barmode='group',
                title="Precipitation Probabilities",
                xaxis_title="Cities and Days",
                yaxis_title="Probability (%)",
                template='plotly_white'
            )
        )

    elif parameter == 'temperature':
        if forecast_days != 0:
            x = [f"{data['City']} ({data['Day']})" for data in all_weather_data]
            min_temps = [data['min temperature'] for data in all_weather_data]
            max_temps = [data['max temperature'] for data in all_weather_data]

            figure = go.Figure(
                data=[
                    go.Scatter(name="Min Temperature", x=x, y=min_temps, mode='lines+markers'),
                    go.Scatter(name="Max Temperature", x=x, y=max_temps, mode='lines+markers')
                ],
                layout=go.Layout(
                    title="Temperature Forecast",
                    xaxis_title="Cities and Days",
                    yaxis_title="Temperature (°C)",
                    template='plotly_white'
                )
            )
        else:
            x = [f"{data['City']} ({data['Day']})" for data in all_weather_data]
            min_temps = [data['temperature'] for data in all_weather_data]
            max_temps = [data['real feel temperature'] for data in all_weather_data]

            figure = go.Figure(
                data=[
                    go.Scatter(name="Temperature", x=x, y=min_temps, mode='lines+markers'),
                    go.Scatter(name="Real Feel Temperature", x=x, y=max_temps, mode='lines+markers')
                ],
                layout=go.Layout(
                    title="Temperature Forecast",
                    xaxis_title="Cities and Days",
                    yaxis_title="Temperature (°C)",
                    template='plotly_white'
                )
            )

    elif parameter == 'wind':
        x = [f"{data['City']} ({data['Day']})" for data in all_weather_data]
        wind_speeds = [data['wind speed'] for data in all_weather_data]

        figure = go.Figure(
            data=go.Bar(x=x, y=wind_speeds, marker_color='#2ca02c'),
            layout=go.Layout(
                title="Wind Speed Forecast",
                xaxis_title="Cities and Days",
                yaxis_title="Speed (km/h)",
                template='plotly_white'
            )
        )

    else:
        raise ValueError(f"Invalid parameter selected: {parameter}")

    map_figure = go.Figure()

    first_last_color = 'red'
    middle_color = 'blue'

    for idx, city in enumerate(map_data):
        color = first_last_color if idx == 0 or idx == len(map_data) - 1 else middle_color
        map_figure.add_trace(go.Scattermapbox(
            lat=[city["lat"]],
            lon=[city["lon"]],
            mode="markers",
            marker=dict(size=10, color=color),
            text=city["city"],
            hoverinfo="text"
        ))

    map_figure.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=50, lon=10),
            zoom=3
        ),
        title="Weather Route Map"
    )

    return figure, map_figure


if __name__ == '__main__':
    app.run_server(debug=True)
