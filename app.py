from flask import Flask, request, render_template
from main import get_weather, get_weather_data, check_bad_weather, get_coordinates_from_city

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check_weather', methods=['POST'])
def check_weather():
    try:
        start_city = request.form.get('start_city')
        end_city = request.form.get('end_city')

        start_lat, start_lon, start_key = get_coordinates_from_city(start_city)
        end_lat, end_lon, end_key = get_coordinates_from_city(end_city)

        start_weather = get_weather_data(get_weather(start_lat, start_lon))
        end_weather = get_weather_data(get_weather(end_lat, end_lon))

        start_status = check_bad_weather(
            start_weather["min temperature"],
            start_weather["max temperature"],
            start_weather["wind speed"],
            start_weather["snow probability"],
            start_weather["rain probability"]
        )
        end_status = check_bad_weather(
            end_weather["min temperature"],
            end_weather["max temperature"],
            end_weather["wind speed"],
            end_weather["snow probability"],
            end_weather["rain probability"]
        )

        # Отображение результата
        return render_template('results.html',
                               start_city=start_city,
                               end_city=end_city,
                               start_status=start_status,
                               end_status=end_status)

    except Exception as e:
        # Обработка ошибок
        return render_template('errors.html', error_message=str(e))

if __name__ == '__main__':
    app.run(debug=True)
