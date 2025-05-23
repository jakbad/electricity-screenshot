from flask import Flask, send_file
import matplotlib.pyplot as plt
import requests
from io import BytesIO
from datetime import datetime
import os

app = Flask(__name__)

def generate_plot(save_path=None):
    url = "https://api.energidataservice.dk/dataset/Elspotprices?limit=24&filter={\"PriceArea\":\"DK2\"}&sort=HourUTC DESC"
    response = requests.get(url)
    data = response.json().get("records", [])

    # Sort by HourUTC ascending
    data.sort(key=lambda x: x["HourUTC"])

    times = [datetime.fromisoformat(rec["HourUTC"]).strftime("%H:%M") for rec in data]
    prices = [rec["SpotPriceDKK"] for rec in data]

    plt.figure(figsize=(6, 4.48), dpi=100)
    plt.plot(times, prices, marker='o')
    plt.title("Electricity Prices (DKK/MWh)", fontsize=14)
    plt.xlabel("Time (UTC)", fontsize=12)
    plt.ylabel("Price", fontsize=12)
    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(fontsize=10)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, format='png')
    else:
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
        return buf

    plt.close()

@app.route("/")
def graph_preview():
    buf = generate_plot()
    return send_file(buf, mimetype='image/png')

@app.route("/refresh")
def refresh():
    os.makedirs("static", exist_ok=True)
    generate_plot(save_path="static/graph.png")
    return "Graph updated!"

@app.route("/image")
def get_image():
    return send_file("static/graph.png", mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
