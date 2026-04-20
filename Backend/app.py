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
# 🔥 PATHS
# ==============================

SAT_MODEL_PATH = "cyclone_detection_model.keras"
MODEL_PATH = "cloud.weights.h5"

satellite_model = None
cloud_model = None

# ==============================
# 📥 GOOGLE DRIVE DOWNLOAD FIX
# ==============================

def download_file_from_google_drive(file_id, destination):
    URL = "https://drive.google.com/uc?export=download"
    session = requests.Session()

    response = session.get(URL, params={"id": file_id}, stream=True)

    # Handle large file confirmation
    for key, value in response.cookies.items():
        if key.startswith("download_warning"):
            params = {"id": file_id, "confirm": value}
            response = session.get(URL, params=params, stream=True)
            break

    with open(destination, "wb") as f:
        for chunk in response.iter_content(1024 * 1024):
            if chunk:
                f.write(chunk)

# ==============================
# 📡 LOAD SATELLITE MODEL (LAZY)
# ==============================

def load_satellite_model():
    global satellite_model

    if satellite_model is None:
        if not os.path.exists(SAT_MODEL_PATH):
            print("Downloading satellite model...")
            download_file_from_google_drive(
                "1cI6MyyUXhz14jNavYqQQdoSeRYKhHWHb",
                SAT_MODEL_PATH
            )

        if os.path.getsize(SAT_MODEL_PATH) < 1000000:
            raise Exception("Satellite model corrupted ❌")

        satellite_model = tf.keras.models.load_model(SAT_MODEL_PATH)
        print("Satellite model loaded ✅")

# ==============================
# ☁️ LOAD CLOUD MODEL (LAZY)
# ==============================

def load_cloud_model():
    global cloud_model

    if cloud_model is None:
        if not os.path.exists(MODEL_PATH):
            print("Downloading cloud model...")
            download_file_from_google_drive(
                "1Vw3wiyGVLWAJYbUBFcuFZ_Mu4B2UfZ6k",
                MODEL_PATH
            )

        if os.path.getsize(MODEL_PATH) < 1000000:
            raise Exception("Cloud model corrupted ❌")

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

        model.load_weights(MODEL_PATH)
        cloud_model = model
        print("Cloud model loaded ✅")

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
# 🌦️ WEATHER API
# ==============================

def get_weather(lat, lon):
    API_KEY = os.environ.get("API_KEY")

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
# 🏠 HOME
# ==============================

@app.route("/")
def home():
    return "🚀 API Running Successfully"

# ==============================
# 🛰️ SATELLITE ROUTE
# ==============================

@app.route("/predict-satellite", methods=["POST"])
def predict_satellite():
    try:
        load_satellite_model()

        file = request.files.get("file")
        if not file:
            return jsonify({"error": "No file"})

        img = Image.open(file).convert("RGB").resize((150,150))
        img_array = np.array(img)/255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = float(satellite_model.predict(img_array, verbose=0)[0][0])

        result = "No Cyclone" if prediction >= 0.5 else "Cyclone"
        confidence = prediction if prediction >= 0.5 else 1 - prediction

        return jsonify({
            "prediction": result,
            "confidence": round(confidence * 100, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# ==============================
# 🔮 MAIN ROUTE
# ==============================

@app.route("/predict", methods=["POST"])
def predict():
    try:
        load_cloud_model()

        file = request.files.get("file")
        lat = request.form.get("lat")
        lon = request.form.get("lon")

        if not file or not lat or not lon:
            return jsonify({"error": "Missing input"})

        lat, lon = float(lat), float(lon)

        img = Image.open(file).convert("RGB").resize((224,224))

        if not is_cloud_image(img):
            return jsonify({"prediction": "Invalid Image", "confidence": 0})

        img_array = np.array(img)/255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = cloud_model.predict(img_array)[0]
        index = int(np.argmax(prediction))
        confidence = float(prediction[index]) * 100

        classes = ['VEIL CLOUDS', 'clear', 'pattern', 'thick dark', 'thick white']
        result = classes[index]

        weather = get_weather(lat, lon)

        return jsonify({
            "prediction": result,
            "confidence": round(confidence, 2),
            "weather": weather
        })

    except Exception as e:
        return jsonify({"error": str(e)})

# ==============================
# 🚀 RUN
# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)