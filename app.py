from flask import Flask, send_file
import matplotlib.pyplot as plt
import requests
from io import BytesIO
from datetime import datetime
import os

app = Flask(__name__)


def generate_plot(save_path=None, nuclear_ref_kwh=0.3):
    # Fetch a large enough window
    url = "https://api.energidataservice.dk/dataset/Elspotprices?limit=100&filter={\"PriceArea\":\"DK2\"}&sort=HourUTC DESC"
    response = requests.get(url)
    all_data = response.json().get("records", [])

    # Parse and sort by HourUTC ascending
    all_data = sorted(all_data, key=lambda x: x["HourUTC"])
    all_data = [rec for rec in all_data if "HourUTC" in rec and "SpotPriceDKK" in rec]

    # Determine time window
    latest_time = max(datetime.fromisoformat(rec["HourUTC"]) for rec in all_data)
    day_before = (datetime.utcnow() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)

    # Filter to time window
    data = [
        rec for rec in all_data
        if day_before <= datetime.fromisoformat(rec["HourUTC"]) <= latest_time
    ]

    # Extract time and price
    times_raw = [datetime.fromisoformat(rec["HourUTC"]) for rec in data]
    times = [t.strftime("%H:%M %d/%m") for t in times_raw]
    prices = [rec["SpotPriceDKK"] / 1000 for rec in data]  # DKK/kWh

    # Begin plot
    timestamp = f"Prices: {day_before.strftime('%d/%m')} – {latest_time.strftime('%d/%m %H:%M')} (UTC)"

    plt.figure(figsize=(6, 4.48), dpi=100)
    plt.plot(times, prices, marker='o', linestyle='-', color='black', label='Electricity Price')

    # Nuclear reference line
    plt.axhline(y=nuclear_ref_kwh, color='gray', linestyle='--', linewidth=1)
    plt.text(len(times) - 1.5, nuclear_ref_kwh + 0.01, f'Nuclear Ref ({nuclear_ref_kwh:.2f} DKK/kWh)', fontsize=8, color='gray', ha='right')

    # Min/max horizontal lines
    min_val = min(prices)
    max_val = max(prices)
    plt.hlines(min_val, 0, prices.index(min_val), colors='blue', linestyles='--', linewidth=1)
    plt.hlines(max_val, 0, prices.index(max_val), colors='red', linestyles='--', linewidth=1)
    plt.text(0, min_val, f'Min: {min_val:.3f}', va='bottom', fontsize=8, color='blue')
    plt.text(0, max_val, f'Max: {max_val:.3f}', va='top', fontsize=8, color='red')

    # Labels
    plt.title(timestamp, fontsize=12)
    plt.xlabel("Time (UTC)", fontsize=10)
    plt.ylabel("Price (DKK/kWh)", fontsize=10)
    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(fontsize=8)
    plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()

    # Output
    if save_path:
        plt.savefig(save_path, format='png', dpi=100)
    else:
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
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
