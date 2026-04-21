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
            return None

        data = res.json()

        return {
            "windSpeed": data["wind"]["speed"],
            "pressure": data["main"]["pressure"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["main"]
        }
    except:
        return None

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
        file = request.files.get("file")

        if not file:
            return jsonify({"error": "No file"})

        # Reset file pointer
        file.seek(0)

        response = requests.post(
            f"{MODEL_SERVER}/satellite",
            files={"file": file},
            timeout=15
        )

        if response.status_code != 200:
            return jsonify({"error": "Model server error"})

        return jsonify(response.json())

    except Exception as e:
        return jsonify({"error": str(e)})

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
            return jsonify({"error": "Missing input"})

        lat, lon = float(lat), float(lon)

        # Validate image
        img = Image.open(file).convert("RGB").resize((224, 224))

        if not is_cloud_image(img):
            return jsonify({
                "prediction": "Invalid Image",
                "confidence": 0
            })

        # Reset file pointer (VERY IMPORTANT)
        file.seek(0)

        # Send to model server
        response = requests.post(
            f"{MODEL_SERVER}/cloud",
            files={"file": file},
            timeout=15
        )

        if response.status_code != 200:
            return jsonify({"error": "Model server error"})

        model_result = response.json()

        prediction = model_result.get("prediction", "Unknown")
        confidence = model_result.get("confidence", 0)

        # Get weather
        weather = get_weather(lat, lon)

        return jsonify({
            "prediction": prediction,
            "confidence": confidence,
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