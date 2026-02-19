from flask import Flask, request, jsonify, send_from_directory
import requests
import os

app = Flask(__name__, static_folder=".")


def get_suggestions(temp_c):
    clothing, accessories, travel, health = [], [], [], []

    if temp_c < 0:
        clothing = ["Heavy thermal jacket", "Insulated inner layers", "Waterproof outer shell", "Snow boots"]
        accessories = ["Insulated gloves", "Wool balaclava", "Thermal scarf", "Hand warmers"]
        travel = ["Carry emergency blanket", "Check road conditions before driving", "Avoid travelling alone in remote areas"]
        health = ["Limit skin exposure to under 10 minutes", "Watch for frostbite signs", "Stay hydrated — cold air dehydrates"]
    elif temp_c < 10:
        clothing = ["Heavy winter jacket", "Wool sweater", "Thermal base layer", "Warm trousers"]
        accessories = ["Knit gloves", "Warm beanie", "Scarf", "Thick socks"]
        travel = ["Allow extra travel time", "Roads may be slippery", "Keep vehicle emergency kit stocked"]
        health = ["Protect extremities", "Warm up gradually after being outdoors", "Vitamin D supplement recommended"]
    elif temp_c < 20:
        clothing = ["Light jacket or hoodie", "Full-sleeve shirt", "Jeans or chinos", "Comfortable sneakers"]
        accessories = ["Light scarf", "Watch for wind-chill", "Carry a compact umbrella"]
        travel = ["Ideal conditions for most travel", "Evening temperatures may drop — layer up"]
        health = ["Good conditions for outdoor exercise", "Stay hydrated", "Check pollen count if allergic"]
    elif temp_c < 30:
        clothing = ["T-shirt or light shirt", "Shorts or light trousers", "Breathable footwear"]
        accessories = ["Sunglasses", "Light cap or hat", "Water bottle"]
        travel = ["Excellent travel conditions", "UV index may be moderate — apply SPF 30+"]
        health = ["30 mins outdoor exercise is safe", "Stay hydrated — 2–3 litres per day", "Watch for heat rash if humid"]
    else:
        clothing = ["Loose cotton clothes", "Light linen shirt", "Moisture-wicking fabrics", "Open sandals or breathable shoes"]
        accessories = ["Polarised sunglasses", "Wide-brim hat", "High-SPF sunscreen (50+)", "Insulated water bottle"]
        travel = ["Avoid outdoor travel 11am–3pm peak heat", "Plan activities for early morning or evening", "Never leave children or pets in parked vehicles"]
        health = ["Drink water every 30 minutes", "Watch for heat exhaustion symptoms", "Cool showers help regulate body temp", "Seek shade frequently"]

    return {"clothing": clothing, "accessories": accessories, "travel": travel, "health": health}


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(".", filename)


@app.route("/get-weather", methods=["POST"])
def get_weather():
    data = request.get_json()
    city = data.get("city", "").strip()

    if not city:
        return jsonify({"error": "City name is required."}), 400

    try:
        url = f"https://wttr.in/{requests.utils.quote(city)}?format=j1"
        resp = requests.get(url, timeout=10, headers={"User-Agent": "WeatherIntelligence/1.0"})

        if resp.status_code != 200:
            return jsonify({"error": "City not found or weather service unavailable."}), 404

        weather_json = resp.json()
        current = weather_json["current_condition"][0]

        temp_c = int(current["temp_C"])
        feels_like = int(current["FeelsLikeC"])
        humidity = int(current["humidity"])
        wind_kmph = int(current["windspeedKmph"])
        description = current["weatherDesc"][0]["value"]

        nearest_area = weather_json["nearest_area"][0]
        resolved_city = nearest_area["areaName"][0]["value"]
        country = nearest_area["country"][0]["value"]

        suggestions = get_suggestions(temp_c)

        return jsonify({
            "city": resolved_city,
            "country": country,
            "temperature": temp_c,
            "feels_like": feels_like,
            "description": description,
            "humidity": humidity,
            "wind_kmph": wind_kmph,
            "suggestions": suggestions,
        })

    except requests.exceptions.Timeout:
        return jsonify({"error": "Weather service timed out. Try again."}), 503
    except (KeyError, ValueError, requests.exceptions.JSONDecodeError):
        return jsonify({"error": "City not found or weather service unavailable."}), 404
    except Exception:
        return jsonify({"error": "An unexpected error occurred. Please try again."}), 500


if __name__ == "__main__":
    app.run(debug=False, port=5000)
