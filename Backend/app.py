from flask import Flask, request, jsonify
import numpy as np
from PIL import Image
from flask_cors import CORS
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense
import os
import requests

app = Flask(__name__)
CORS(app)

print("🚀 Loading models...")

# =========================
# 🛰️ LOAD SATELLITE MODEL
# =========================
satellite_model = tf.keras.models.load_model("cyclone_detection_model.keras")

# =========================
# ☁️ LOAD CLOUD MODEL
# =========================
cloud_model = Sequential([
    Input(shape=(224, 224, 3)),
    Conv2D(32, (3,3), activation='relu'),
    MaxPooling2D(2,2),

    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(2,2),

    Conv2D(128, (3,3), activation='relu'),
    MaxPooling2D(2,2),

    Flatten(),
    Dense(128, activation='relu'),
    Dense(5, activation='softmax')
])

cloud_model.load_weights("cloud.weights.h5")

print("✅ Models loaded successfully")

# =========================
# ☁️ IMAGE VALIDATION
# =========================
def is_cloud_image(img):
    img_np = np.array(img)

    brightness = np.mean(img_np)
    blue_mean = np.mean(img_np[:, :, 2])
    red_mean = np.mean(img_np[:, :, 0])

    if brightness < 50:
        return False

    if blue_mean < red_mean:
        return False

    return True

# =========================
# 🌦️ WEATHER API
# =========================
def get_weather(lat, lon):
    API_KEY = "8bfb8223a3b94f6137c3b569e06ddda0"   # 🔥 paste your key directly here

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    try:
        res = requests.get(url, timeout=10)

       
        # ✅ CORRECT PLACE (AFTER res is created)
        print("Status Code:", res.status_code)
        print("Response:", res.text)
        if res.status_code != 200:
            return None

        data = res.json()
        

        return {
            "windSpeed": data["wind"]["speed"] * 3.6,  # convert m/s → km/h
            "pressure": data["main"]["pressure"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["main"]
        }

    except Exception as e:
        print("Weather Exception:", str(e))
        return None

# =========================
# 🧠 RISK CALCULATION
# =========================
def calculate_risk(prediction, wind, humidity):
    risk = "Low"

    if "dark" in prediction or "pattern" in prediction:
        risk = "High"
    elif "veil" in prediction:
        risk = "Medium"

    if wind and wind > 10:
        risk = "High"

    if humidity and humidity > 80:
        risk = "High"

    return risk

def calculate_rain_chance(condition, humidity):
    if not condition:
        return "Unknown"

    condition = condition.lower()

    if "rain" in condition or "storm" in condition:
        return "High"

    if humidity and humidity > 70:
        return "Medium"

    return "Low"

# =========================
# 🏠 HOME
# =========================
@app.route("/")
def home():
    return "🚀 Server Running"

# =========================
# 🔮 MAIN ROUTE
# =========================
@app.route("/predict", methods=["POST"])
def predict():
    try:
        file = request.files.get("file")
        lat = request.form.get("lat")
        lon = request.form.get("lon")

        # ❌ Missing input
        if not file or not lat or not lon:
            return jsonify({
                "success": False,
                "message": "Missing input",
                "prediction": None,
                "confidence": 0,
                "weather": {},
                "riskLevel": "Unknown",
                "rainChance": "Unknown"
            })

        lat, lon = float(lat), float(lon)

        # 📷 Process image
        img = Image.open(file).convert("RGB").resize((224,224))

        # 🤖 Model prediction
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = cloud_model.predict(img_array, verbose=0)[0]
        index = int(np.argmax(prediction))
        confidence = float(prediction[index]) * 100

        classes = ['VEIL CLOUDS', 'clear', 'pattern', 'thick dark', 'thick white']
        result = classes[index]

        # 🌦 Weather
        weather = get_weather(lat, lon)

        if not weather:
            print("⚠️ Weather API failed")
            weather = {
                "windSpeed": 0,
                "pressure": 0,
                "humidity": 0,
                "condition": "Unknown"
            }

        # 🌪️ WIND-BASED CYCLONE RISK
        def calculate_risk_wind_only(wind):
            if wind is None:
                return "Unknown"

            if wind >= 120:
                return "Very High"
            elif wind >= 90:
                return "High"
            elif wind >= 60:
                return "Medium"
            elif wind >= 30:
                return "Low"
            else:
                return "Very Low"

        # 🌧️ RAIN CHANCE
        def calculate_rain_chance(condition, humidity):
            if not condition:
                return "Unknown"

            condition = condition.lower()

            if "rain" in condition or "storm" in condition:
                return "High"

            if humidity > 70:
                return "Medium"

            return "Low"

        # ✅ Apply logic
        risk = calculate_risk_wind_only(weather["windSpeed"])
        rainChance = calculate_rain_chance(
            weather["condition"],
            weather["humidity"]
        )

        # ✅ Final response
        return jsonify({
            "success": True,
            "prediction": result,
            "confidence": round(confidence, 2),
            "weather": weather,
            "riskLevel": risk,
            "rainChance": rainChance
        })

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({
            "success": False,
            "message": "Server error",
            "prediction": None,
            "confidence": 0,
            "weather": {},
            "riskLevel": "Unknown",
            "rainChance": "Unknown"
        })
    
    # =========================
# 🛰️ SATELLITE ROUTE
# =========================
@app.route("/satellite", methods=["POST"])
def satellite():
    try:
        file = request.files.get("file")

        if not file:
            return jsonify({
                "success": False,
                "message": "No file provided"
            })

        # 📷 Process image (IMPORTANT: correct size)
        img = Image.open(file).convert("RGB").resize((150,150))

        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # 🤖 Model prediction
        prediction = float(satellite_model.predict(img_array, verbose=0)[0][0])

        # 🎯 Result logic
        if prediction < 0.5:
            result = "Cyclone Detected"
            confidence = (1 - prediction) * 100
        else:
            result = "No Cyclone"
            confidence = prediction * 100

        return jsonify({
            "success": True,
            "prediction": result,
            "confidence": round(confidence, 2)
        })

    except Exception as e:
        print("Satellite Error:", str(e))
        return jsonify({
            "success": False,
            "message": "Server error"
        })
        

# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)