from flask import Flask, request, jsonify
import numpy as np
from PIL import Image
from flask_cors import CORS
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense
import os
import requests

# 🔒 Disable GPU (Render safe)
tf.config.set_visible_devices([], 'GPU')

app = Flask(__name__)
CORS(app)

# =========================
# 📁 BASE DIRECTORY
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================
# ⬇️ DOWNLOAD FUNCTION (FIXED)
# =========================
def download_file(url, filename):
    filepath = os.path.join(BASE_DIR, filename)

    if not os.path.exists(filepath):
        print(f"⬇ Downloading {filename}...")

        session = requests.Session()
        response = session.get(url, stream=True)

        # Handle Google Drive confirm page
        for key, value in response.cookies.items():
            if key.startswith("download_warning"):
                confirm_url = url + "&confirm=" + value
                response = session.get(confirm_url, stream=True)

        if response.status_code != 200:
            raise Exception(f"Failed to download {filename}")

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(1024):
                if chunk:
                    f.write(chunk)

        print(f"✅ Downloaded {filename}")

    return filepath

# =========================
# 🔗 MODEL LINKS
# =========================
MODEL_URL = "https://drive.google.com/uc?id=1Vw3wiyGVLWAJYbUBFcuFZ_Mu4B2UfZ6k"
WEIGHTS_URL = "https://drive.google.com/uc?id=1cI6MyyUXhz14jNavYqQQdoSeRYKhHWHb"

# =========================
# ⚡ GLOBAL MODEL FLAGS (IMPORTANT)
# =========================
model_path = None
weights_path = None

satellite_model = None
cloud_model_loaded = False

# =========================
# ☁️ CLOUD MODEL STRUCTURE
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

# =========================
# 🌦️ WEATHER API
# =========================
def get_weather(lat, lon):
    API_KEY = os.getenv("OPENWEATHER_API_KEY")

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    try:
        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            return None

        data = res.json()

        return {
            "windSpeed": data["wind"]["speed"] * 3.6,
            "pressure": data["main"]["pressure"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["main"]
        }

    except Exception as e:
        print("Weather Exception:", str(e))
        return None

# =========================
# 🧠 RISK LOGIC
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
    global cloud_model_loaded, weights_path

    try:
        file = request.files.get("file")
        lat = request.form.get("lat")
        lon = request.form.get("lon")

        if not file or not lat or not lon:
            return jsonify({
                "success": False,
                "message": "Missing input"
            })

        lat, lon = float(lat), float(lon)

        # 🔥 Lazy load cloud model
        if not cloud_model_loaded:
            print("🔄 Loading cloud model...")
            weights_path = download_file(WEIGHTS_URL, "cloud.weights.h5")
            cloud_model.load_weights(weights_path)
            cloud_model_loaded = True

        img = Image.open(file).convert("RGB").resize((224,224))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = cloud_model.predict(img_array, verbose=0)[0]
        index = int(np.argmax(prediction))
        confidence = float(prediction[index]) * 100

        classes = ['VEIL CLOUDS', 'clear', 'pattern', 'thick dark', 'thick white']
        result = classes[index]

        weather = get_weather(lat, lon) or {
            "windSpeed": 0,
            "pressure": 0,
            "humidity": 0,
            "condition": "Unknown"
        }

        risk = calculate_risk(result, weather["windSpeed"], weather["humidity"])
        rainChance = calculate_rain_chance(weather["condition"], weather["humidity"])

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
        return jsonify({"success": False, "message": "Server error"})

# =========================
# 🛰️ SATELLITE ROUTE
# =========================
@app.route("/satellite", methods=["POST"])
def satellite():
    global satellite_model, model_path

    try:
        file = request.files.get("file")

        if not file:
            return jsonify({"success": False, "message": "No file provided"})

        # 🔥 Lazy load satellite model
        if satellite_model is None:
            print("🔄 Loading satellite model...")
            model_path = download_file(MODEL_URL, "cyclone_detection_model.keras")
            satellite_model = tf.keras.models.load_model(model_path)

        img = Image.open(file).convert("RGB").resize((150,150))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = float(satellite_model.predict(img_array, verbose=0)[0][0])

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
        return jsonify({"success": False, "message": "Server error"})

# =========================
# 🚀 RUN (LOCAL ONLY)
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)