from flask import Flask, request, jsonify
import numpy as np
from PIL import Image
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# ==============================
# 🌐 MODEL SERVER (Colab ngrok URL)
# ==============================
MODEL_SERVER = "https://alfalfa-caption-email.ngrok-free.dev"

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

    try:
        res = requests.get(url, timeout=10)

        if res.status_code != 200:
            print("Weather API error:", res.text)
            return None

        data = res.json()

        return {
            "windSpeed": data["wind"]["speed"],
            "pressure": data["main"]["pressure"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["main"]
        }

    except Exception as e:
        print("Weather Exception:", str(e))
        return None

# ==============================
# 🏠 HOME
# ==============================
@app.route("/")
def home():
    return "🚀 API Running Successfully"

# ==============================
# 🛰️ SATELLITE ROUTE (SAFE)
# ==============================
@app.route("/predict-satellite", methods=["POST"])
def predict_satellite():
    try:
        file = request.files.get("file")

        if not file:
            return jsonify({
                "prediction": "Error",
                "confidence": 0,
                "weather": None
            })

        file.seek(0)

        response = requests.post(
            f"{MODEL_SERVER}/satellite",
            files={"file": file},
            timeout=30
        )

        if response.status_code != 200:
            print("Satellite API error:", response.text)
            return jsonify({
                "prediction": "Error",
                "confidence": 0,
                "weather": None
            })

        data = response.json()
        print("Satellite Response:", data)

        return jsonify({
            "prediction": data.get("prediction", "Unknown"),
            "confidence": data.get("confidence", 0),
            "weather": None
        })

    except Exception as e:
        print("Satellite Exception:", str(e))
        return jsonify({
            "prediction": "Error",
            "confidence": 0,
            "weather": None
        })

# ==============================
# 🔮 MAIN ROUTE (CLOUD + WEATHER)
# ==============================
@app.route("/predict", methods=["POST"])
def predict():
    try:
        file = request.files.get("file")
        lat = request.form.get("lat")
        lon = request.form.get("lon")

        if not file or not lat or not lon:
            return jsonify({
                "prediction": "Error",
                "confidence": 0,
                "weather": None
            })

        lat, lon = float(lat), float(lon)

        # Validate image
        img = Image.open(file).convert("RGB").resize((224, 224))

        if not is_cloud_image(img):
            return jsonify({
                "prediction": "Invalid Image",
                "confidence": 0,
                "weather": None
            })

        # Reset file pointer
        file.seek(0)

        # Call cloud model
        try:
            response = requests.post(
                f"{MODEL_SERVER}/cloud",
                files={"file": file},
                timeout=30
            )
        except Exception as e:
            print("Cloud API connection failed:", str(e))
            return jsonify({
                "prediction": "Error",
                "confidence": 0,
                "weather": None
            })

        if response.status_code != 200:
            print("Cloud API error:", response.text)
            return jsonify({
                "prediction": "Error",
                "confidence": 0,
                "weather": None
            })

        model_result = response.json()
        print("Cloud Model Response:", model_result)

        prediction = model_result.get("prediction", "Unknown")
        confidence = model_result.get("confidence", 0)

        # Weather data
        weather = get_weather(lat, lon)

        return jsonify({
            "prediction": prediction,
            "confidence": confidence,
            "weather": weather
        })

    except Exception as e:
        print("Main Exception:", str(e))
        return jsonify({
            "prediction": "Error",
            "confidence": 0,
            "weather": None
        })

# ==============================
# 🚀 RUN
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)