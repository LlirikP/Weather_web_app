from flask import Flask, request, render_template, flash, redirect, url_for
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
        if not start_lat:
            flash("Неверно введён начальный город.", "error")
            return redirect(url_for('index'))

        end_lat, end_lon, end_key = get_coordinates_from_city(end_city)
        if not end_lat:
            flash("Неверно введён конечный город.", "error")
            return redirect(url_for('index'))

        start_weather = get_weather_data(get_weather(start_lat, start_lon))
        if not start_weather:
            flash("Ошибка получения данных о погоде для начального города.", "error")
            return redirect(url_for('index'))

        end_weather = get_weather_data(get_weather(end_lat, end_lon))
        if not end_weather:
            flash("Ошибка получения данных о погоде для конечного города.", "error")
            return redirect(url_for('index'))

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

        return render_template('results.html',
                               start_city=start_city,
                               end_city=end_city,
                               start_status=start_status,
                               end_status=end_status)

    except Exception as e:
        return render_template('errors.html', error_message=str(e))


if __name__ == '__main__':
    app.run(debug=True)
