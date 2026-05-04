from flask import Flask, request, jsonify
import numpy as np
from PIL import Image
from flask_cors import CORS
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense
import os
import requests

# 🔒 Disable GPU
tf.config.set_visible_devices([], 'GPU')

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================
# 🔥 DOWNLOAD FUNCTION (FIXED)
# =========================
def download_file(url, filename):
    filepath = os.path.join(BASE_DIR, filename)

    if not os.path.exists(filepath):
        print(f"⬇ Downloading {filename}...")

        response = requests.get(url, stream=True, timeout=60)

        if response.status_code != 200:
            raise Exception(f"❌ Download failed: {filename}")

        with open(filepath, "wb") as f:
            for chunk in response.iter_content(1024):
                if chunk:
                    f.write(chunk)

        # 🔥 Validate file
        size = os.path.getsize(filepath)
        print(f"📦 File size: {size}")

        if size < 100000:  # <100KB = invalid
            os.remove(filepath)
            raise Exception(f"❌ Invalid file downloaded: {filename}")

        print(f"✅ Downloaded {filename}")

    return filepath


# =========================
# 🔥 MODEL URLS (CORRECT)
# =========================
MODEL_URL = "https://github.com/karthik90100/Cyclone_Detection_Mobile_App/releases/download/v1/cyclone_detection_model.keras"
WEIGHTS_URL = "https://github.com/karthik90100/Cyclone_Detection_Mobile_App/releases/download/v1/cloud.weights.h5"


# =========================
# GLOBAL MODELS
# =========================
satellite_model = None
cloud_model_loaded = False


# =========================
# CLOUD MODEL ARCHITECTURE
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
# WEATHER API
# =========================
def get_weather(lat, lon):
    API_KEY = os.getenv("OPENWEATHER_API_KEY")

    if not API_KEY:
        print("⚠ No API key found")
        return None

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
        print("Weather Error:", str(e))
        return None


# =========================
# LOGIC FUNCTIONS
# =========================
def calculate_risk(prediction, wind, humidity):
    if "dark" in prediction or "pattern" in prediction:
        return "High"
    if "veil" in prediction:
        return "Medium"
    if wind and wind > 10:
        return "High"
    if humidity and humidity > 80:
        return "High"
    return "Low"


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
# HOME ROUTE
# =========================
@app.route("/")
def home():
    return "🚀 Server Running"


# =========================
# CLOUD PREDICTION
# =========================
@app.route("/predict", methods=["POST"])
def predict():
    global cloud_model_loaded

    try:
        file = request.files.get("file")
        lat = request.form.get("lat")
        lon = request.form.get("lon")

        if not file or not lat or not lon:
            return jsonify({"success": False, "message": "Missing input"})

        lat, lon = float(lat), float(lon)

        # 🔥 Load weights once
        if not cloud_model_loaded:
            print("🔄 Loading cloud model...")
            weights_path = download_file(WEIGHTS_URL, "cloud.weights.h5")

            print("📦 Checking weights...")
            print("Exists:", os.path.exists(weights_path))
            print("Size:", os.path.getsize(weights_path))

            cloud_model.load_weights(weights_path)
            cloud_model_loaded = True
            print("✅ Cloud model ready")

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

        return jsonify({
            "success": True,
            "prediction": result,
            "confidence": round(confidence, 2),
            "weather": weather,
            "riskLevel": calculate_risk(result, weather["windSpeed"], weather["humidity"]),
            "rainChance": calculate_rain_chance(weather["condition"], weather["humidity"])
        })

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"success": False, "message": str(e)})


# =========================
# SATELLITE PREDICTION
# =========================
@app.route("/satellite", methods=["POST"])
def satellite():
    global satellite_model

    try:
        file = request.files.get("file")

        if not file:
            return jsonify({"success": False, "message": "No file"})

        # 🔥 Load model once
        if satellite_model is None:
            print("🔄 Loading satellite model...")
            model_path = download_file(MODEL_URL, "cyclone_detection_model.keras")

            print("📦 Checking model...")
            print("Exists:", os.path.exists(model_path))
            print("Size:", os.path.getsize(model_path))

            try:
                satellite_model = tf.keras.models.load_model(model_path)
                print("✅ Satellite model loaded")
            except Exception as e:
                print("❌ Model load failed:", str(e))
                raise e

        img = Image.open(file).convert("RGB").resize((150,150))
        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        pred = float(satellite_model.predict(img_array, verbose=0)[0][0])

        return jsonify({
            "success": True,
            "prediction": "Cyclone Detected" if pred < 0.5 else "No Cyclone",
            "confidence": round((1 - pred if pred < 0.5 else pred) * 100, 2)
        })

    except Exception as e:
        print("❌ SAT ERROR:", str(e))
        return jsonify({"success": False, "message": str(e)})


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)