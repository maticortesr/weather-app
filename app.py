from flask import Flask, render_template, request, flash, redirect
import sys
import requests
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, template_folder="templates")
app.secret_key = b'_5#y2Q8z\n\xec]/'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
db = SQLAlchemy(app)
API_KEY = "163c7bfda7813e021647b3a800bd7b7b"
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __repr__(self):
        return self.name


@app.route("/")
def index():
    db.create_all()
    cities = City.query.all()
    weather_info = get_weather_info(cities)
    for city in cities:
        for city_weather in weather_info:
            if city.name.upper() == city_weather['city']:
                city_weather['id'] = city.id
    return render_template('index.html', weather=weather_info)


@app.route('/add', methods=['POST'])
def add_city():
    if request.method == 'POST':
        city_name = request.form['city_name']
        response = requests.post(BASE_URL, params={"q": city_name, "appid": API_KEY})
        response_json = response.json()
        if response_json['cod'] != '404':
            city_exist = City.query.filter_by(name=city_name).first()
            if city_exist is None:
                print("Adding city: ", city_name)
                city = City(name=city_name)
                db.session.add(city)
                db.session.commit()
                return redirect('/')
            else:
                flash("The city has already been added to the list!")
        else:
            flash("The city doesn't exist!")
        return redirect('/')


@app.route('/delete/<city_id>', methods=['GET', 'POST'])
def delete(city_id):
    if request.method == 'POST':
        city = City.query.filter_by(id=city_id).first()
        db.session.delete(city)
        db.session.commit()
        return redirect('/')


def get_weather_info(cities):
    weather_cards = []
    city_names = [x.name for x in cities]
    for city in city_names:
        response = requests.post(BASE_URL, params={"q": city, "appid": API_KEY, 'units':'metric'})
        response_json = response.json()
        weather_info = {"temp": int(response_json['main']['temp']), "city": response_json['name'].upper(),
                        "state": response_json['weather'][0]['main']}
        weather_cards.append(weather_info)
    return weather_cards


# don't change the following way to run flask:
if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        app.run()