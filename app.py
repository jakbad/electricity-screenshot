from flask import Flask, send_file
import matplotlib.pyplot as plt
import requests
from io import BytesIO
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def graph():
    url = "https://api.energidataservice.dk/dataset/Elspotprices?limit=24&filter={\"PriceArea\":\"DK2\"}&sort=HourUTC DESC"
    response = requests.get(url)
    data = response.json().get("records", [])

    # Sort records by HourUTC ascending
    data.sort(key=lambda x: x["HourUTC"])

    times = [datetime.fromisoformat(rec["HourUTC"]).strftime("%H:%M") for rec in data]
    prices = [rec["SpotPriceDKK"] for rec in data]

    # Inky Frame 5.7: 600x448 pixels
    plt.figure(figsize=(6, 4.48), dpi=100)
    plt.plot(times, prices, marker='o')
    plt.title("Electricity Prices (DKK/MWh)", fontsize=14)
    plt.xlabel("Time (UTC)", fontsize=12)
    plt.ylabel("Price", fontsize=12)
    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(fontsize=10)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return send_file(buf, mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
