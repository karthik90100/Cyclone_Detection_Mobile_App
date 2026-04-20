from flask import Flask, request, jsonify
import numpy as np
from PIL import Image
from flask_cors import CORS
import requests
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense
import os

app = Flask(__name__)
CORS(app)

# ==============================
# 🔥 MODEL SETUP
# ==============================

## 📡 Download Satellite Model
SAT_MODEL_PATH = "cyclone_detection_model.keras"

if not os.path.exists(SAT_MODEL_PATH):
    print("Downloading satellite model...")

    url = "https://drive.google.com/uc?export=download&id=1cI6MyyUXhz14jNavYqQQdoSeRYKhHWHb"
    r = requests.get(url, timeout=60)

    if r.status_code == 200:
        with open(SAT_MODEL_PATH, "wb") as f:
            f.write(r.content)
        print("Satellite model downloaded ✅")
    else:
        print("Satellite model download failed ❌")

# Load model
satellite_model = tf.keras.models.load_model(SAT_MODEL_PATH)
# ☁️ Cloud Model
model = Sequential([
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
MODEL_PATH = "cloud.weights.h5"

if not os.path.exists(MODEL_PATH):
    print("Downloading model...")

    url = "https://drive.google.com/uc?export=download&id=1Vw3wiyGVLWAJYbUBFcuFZ_Mu4B2UfZ6k"
    r = requests.get(url, timeout=60)

    if r.status_code == 200:
        with open(MODEL_PATH, "wb") as f:
            f.write(r.content)
        print("Download complete ✅")
    else:
        print("Download failed ❌")

model.load_weights(MODEL_PATH)

classes = ['VEIL CLOUDS', 'clear', 'pattern', 'thick dark', 'thick white']

# ==============================
# ☁️ IMAGE VALIDATION
# ==============================

def is_cloud_image(img):
    img_np = np.array(img)

    brightness = np.mean(img_np)
    blue_mean = np.mean(img_np[:, :, 2])
    red_mean = np.mean(img_np[:, :, 0])

    if brightness < 70:
        return False

    if blue_mean < red_mean:
        return False

    return True

# ==============================
# 🌦️ WEATHER API FUNCTION
# ==============================

def get_weather(lat, lon):
    API_KEY = os.environ.get("API_KEY")  # ✅ FIXED

    if not API_KEY:
        return None

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    res = requests.get(url)

    if res.status_code != 200:
        return None

    data = res.json()

    return {
        "windSpeed": data["wind"]["speed"],
        "pressure": data["main"]["pressure"],
        "humidity": data["main"]["humidity"],
        "condition": data["weather"][0]["main"]
    }

# ==============================
# 🏠 HOME ROUTE
# ==============================

@app.route("/", methods=["GET"])
def home():
    return "🚀 Cloud + Cyclone Detection API Running"

# ==============================
# 🛰️ SATELLITE ROUTE
# ==============================

@app.route("/predict-satellite", methods=["POST"])
def predict_satellite():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"})

        file = request.files["file"]

        img = Image.open(file).convert("RGB")
        img = img.resize((150, 150))

        img_array = np.array(img, dtype=np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = float(satellite_model.predict(img_array, verbose=0)[0][0])

        if prediction >= 0.5:
            result = "No Cyclone"
            confidence = prediction
        else:
            result = "Cyclone"
            confidence = 1 - prediction

        return jsonify({
            "prediction": result,
            "confidence": round(confidence * 100, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# ==============================
# 🔮 MAIN PREDICTION
# ==============================

@app.route("/predict", methods=["POST"])
def predict():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"})

        file = request.files["file"]

        lat = request.form.get("lat")
        lon = request.form.get("lon")

        if not lat or not lon:
            return jsonify({"error": "Location not provided"})

        lat = float(lat)
        lon = float(lon)

        img = Image.open(file).convert("RGB")
        img = img.resize((224, 224))

        if not is_cloud_image(img):
            return jsonify({
                "prediction": "Invalid Image ❌",
                "confidence": 0
            })

        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array)[0]
        index = int(np.argmax(prediction))
        confidence = float(prediction[index]) * 100

        result = classes[index]

        weather = get_weather(lat, lon)

        if weather is None:
            return jsonify({
                "prediction": result,
                "confidence": round(confidence, 2),
                "error": "Weather API failed"
            })

        risk = "🟢 Safe"

        if (
            result.lower() in ["thick dark", "thick white"] and
            weather["windSpeed"] > 15 and
            weather["pressure"] < 1000
        ):
            risk = "🔴 Cyclone Risk"

        elif weather["windSpeed"] > 10:
            risk = "🟡 Storm Possible"

        return jsonify({
            "prediction": result,
            "confidence": round(confidence, 2),
            "weather": weather,
            "risk": risk
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# ==============================
# 🚀 RUN SERVER (FIXED)
# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # ✅ FIXED
    app.run(host="0.0.0.0", port=port)