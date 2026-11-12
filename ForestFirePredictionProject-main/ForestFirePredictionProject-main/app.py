from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
from flask import Flask, render_template, request
from model import predict_fire
from flask import send_file
from datetime import datetime

import requests
import os
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import time

app = Flask(__name__)




import folium

def create_map(lat, lon):
    m = folium.Map(location=[lat, lon], zoom_start=6)

    folium.Marker(
        [lat, lon],
        popup="🔥 Fire Location",
        icon=folium.Icon(color='red')
    ).add_to(m)

    m.save("templates/map.html")




def get_risk_level(prob):
    if prob < 40:
        return "🟢 Low Risk"
    elif prob < 70:
        return "🟡 Medium Risk"
    else:
        return "🔴 High Risk"




@app.route('/map')
def map_view():
    return render_template('map.html')
# 🔥 Home Page
@app.route('/')
def home():
    return render_template('index.html')


# 📊 Graph Function
def create_graph(temp, humidity, rainfall):
    labels = ['Temp', 'Humidity', 'Rainfall']
    values = [temp, humidity, rainfall]

    plt.figure()
    plt.plot(labels, values, marker='o')
    plt.title("Weather Parameters")

    # Save graph
    path = os.path.join('static', 'graph.png')
    plt.savefig(path)
    plt.close()


# 🔥 Prediction Route
@app.route('/predict', methods=['POST'])
def predict():
    try:
        temp = float(request.form['temp'])
        humidity = float(request.form['humidity'])
        rainfall = float(request.form['rainfall'])

        # ✅ Validation
        if temp < 0 or humidity < 0 or rainfall < 0:
            return render_template('index.html', error="Invalid Input")

        result, prob = predict_fire(temp, humidity, rainfall)
        risk = get_risk_level(prob)

        # 📊 Create graph
        create_graph(temp, humidity, rainfall)

        return render_template(
            'index.html',
            result=result,
            prob=prob,
            risk=risk,
            graph=str(int(time.time()))   # 🔥 avoids cache
        )

    except Exception as e:
        return render_template('index.html', error=str(e))
    
history = []

def update_history(t, h, r):
    history.append([t, h, r])
    if len(history) > 5:
        history.pop(0)

# 🌐 Weather API Route
@app.route('/weather', methods=['POST'])
def weather():
    try:
        city = request.form['city']

        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            return render_template('index.html', error="City not found")

        temp = data['main']['temp']
        humidity = data['main']['humidity']

        # ✅ GET LOCATION
        lat = data['coord']['lat']
        lon = data['coord']['lon']

        # ✅ CREATE MAP
        create_map(lat, lon)

        return render_template(
            'index.html',
            temp=temp,
            humidity=humidity,
            city=city,
            lat=lat,
            lon=lon,
            show_map=True,
            autofill=True
        )

    except Exception as e:
        return render_template('index.html', error=str(e))

from flask import send_file
from datetime import datetime

@app.route('/download')
def download():
    result = request.args.get('res')
    prob = request.args.get('prob')

    content = f"""
===============================
   FOREST FIRE REPORT
===============================

Date & Time : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Prediction  : {result}
Probability : {prob}%

--------------------------------
System: Forest Fire Prediction
--------------------------------
"""

    with open("report.txt", "w", encoding="utf-8") as f:
        f.write(content)

    return send_file("report.txt", as_attachment=True)

# 🚀 Run Server
if __name__ == "__main__":
    print("Starting Flask Server...")
    app.run(debug=True)