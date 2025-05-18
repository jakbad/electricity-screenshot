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

    plt.figure(figsize=(10, 4))
    plt.plot(times, prices, marker='o')
    plt.title("Electricity Prices (DKK/MWh)")
    plt.xlabel("Time (UTC)")
    plt.ylabel("Price")
    plt.xticks(rotation=45)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return send_file(buf, mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
