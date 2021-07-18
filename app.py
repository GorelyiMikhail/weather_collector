from flask import Flask, render_template, request
from clients import YandexWeatherForecast, AccuWeatherForecast, YandexGeocoder, WeatherComForecast

app = Flask(__name__)
# Создание необходимых объектов классов
yandex_geocoder_getter = YandexGeocoder.from_api_token_path(
    'yandex_geocoder_token.txt',
)
yandex_weather_getter = YandexWeatherForecast.from_api_token_path(
    'yandex_weather_token.txt',
)
accu_weather_getter = AccuWeatherForecast.from_api_token_path(
    'accu_weather_token.txt',
)

weathercom_weather_getter = WeatherComForecast()


# Рендер формы для запроса
@app.route('/form')
def form():
    return render_template('form.html')


# Рендер ответа на запрос
@app.route('/data', methods=['POST', 'GET'])
def data():
    if request.method == 'GET':
        return f'The URL /data is accessed directly. Try going to "/form" to submit form'
    if request.method == 'POST':
        if request.form['Language'] == 'Русский/Russian':
            language = 'ru'
        elif request.form['Language'] == 'Английский/English':
            language = 'en-US'
        coordinates = yandex_geocoder_getter(request.form['City'])
        yandex_weather = yandex_weather_getter(coordinates)
        accu_weather = accu_weather_getter(language, request.form['City'])
        weathercom_weather = weathercom_weather_getter(coordinates)
        if request.form['Language'] == 'Русский/Russian':
            form_data = {
                'Город': request.form['City'],
                'Температура в данный момент согласно ЯндексПогоде': yandex_weather['cur_t'],
                'Температура в данный момент согласно Weather.com': weathercom_weather['cur_t'],
                'Минимальная температура': accu_weather['min_t'],
                'Максимальная температура': accu_weather['max_t'],
                'Температура утром': weathercom_weather['mor_t'],
                'Температура днем': weathercom_weather['day_t'],
                'Температура вечером': weathercom_weather['evn_t'],
                'Температура ночью': weathercom_weather['nig_t'],
            }
        elif request.form['Language'] == 'Английский/English':
            form_data = {
                'City': request.form['City'],
                'Current temperature according to YandexWeather': yandex_weather['cur_t'],
                'Current temperature according to Weather.com': weathercom_weather['cur_t'],
                'Lowest temperature': accu_weather['min_t'],
                'Highest temperature': accu_weather['max_t'],
                'Morning temperature': weathercom_weather['mor_t'],
                'Daytime temperature': weathercom_weather['day_t'],
                'Evening temperature': weathercom_weather['evn_t'],
                'Night temperature': weathercom_weather['nig_t'],
            }
        return render_template('data.html', form_data=form_data)


# Запуск веб приложения
if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
