from flask import Flask, send_file
import matplotlib.pyplot as plt
import requests
from io import BytesIO
from datetime import datetime, timedelta
import os



app = Flask(__name__)

def generate_plot_old(save_path=None, nuclear_ref=300):
    url = "https://api.energidataservice.dk/dataset/Elspotprices?limit=24&filter={\"PriceArea\":\"DK2\"}&sort=HourUTC DESC"
    response = requests.get(url)
    data = response.json().get("records", [])

    # Sort by HourUTC ascending
    data.sort(key=lambda x: x["HourUTC"])

    times_raw = [datetime.fromisoformat(rec["HourUTC"]) for rec in data]
    times = [t.strftime("%H:%M %d/%m") for t in times_raw]
    prices = [rec["SpotPriceDKK"] for rec in data]

    timestamp = datetime.now().strftime("Prices as of: %Y-%m-%d %H:%M")

    plt.figure(figsize=(6, 4.48), dpi=100)
    plt.plot(times, prices, marker='o', linestyle='-', color='black', label='Electricity Price')

    # Nuclear reference line
    plt.axhline(y=nuclear_ref, color='gray', linestyle='--', linewidth=1)
    plt.text(len(times) - 1.5, nuclear_ref + 10, f'Nuclear Ref ({nuclear_ref} DKK/MWh)', fontsize=8, color='gray', ha='right')

    # Annotate min and max with horizontal lines to y-axis
    min_val = min(prices)
    max_val = max(prices)
    plt.hlines(min_val, 0, prices.index(min_val), colors='blue', linestyles='--', linewidth=1)
    plt.hlines(max_val, 0, prices.index(max_val), colors='red', linestyles='--', linewidth=1)
    plt.text(0, min_val, f'Min: {min_val:.1f}', va='bottom', fontsize=8, color='blue')
    plt.text(0, max_val, f'Max: {max_val:.1f}', va='top', fontsize=8, color='red')

    plt.title(timestamp, fontsize=12)
    plt.xlabel("Time (UTC)", fontsize=10)
    plt.ylabel("Price (DKK/MWh)", fontsize=10)
    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(fontsize=8)
    plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, format='jpg', dpi=100)
    else:
        buf = BytesIO()
        plt.savefig(buf, format='jpg', dpi=100)
        buf.seek(0)
        plt.close()
        return buf

    plt.close()


def generate_plot(save_path=None, nuclear_ref=300):
    # Fetch more data to get 48+ hours
    url = "https://api.energidataservice.dk/dataset/Elspotprices?limit=100&filter={\"PriceArea\":\"DK2\"}&sort=HourUTC DESC"
    response = requests.get(url)
    records = response.json().get("records", [])

    # Sort chronologically
    records.sort(key=lambda x: x["HourUTC"])

    # Define time window: from midnight 1 days ago to latest available
    now = datetime.utcnow()
    start_time = (now - timedelta(days=0)).replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = max(datetime.fromisoformat(r["HourUTC"]) for r in records)

    filtered = [
        r for r in records
        if start_time <= datetime.fromisoformat(r["HourUTC"]) <= end_time
    ]

    times_raw = [datetime.fromisoformat(r["HourUTC"]) for r in filtered]
    times = [t.strftime("%d\n%H") for t in times_raw]  # X-axis: DD on top, HH below
    prices = [r["SpotPriceDKK"] for r in filtered]

    timestamp = f"Prices: {start_time.strftime('%d/%m')} – {end_time.strftime('%d/%m %H:%M')} (UTC)"

    plt.figure(figsize=(6, 4.48), dpi=100)
    plt.plot(times, prices, marker='o', linestyle='-', color='black', label='Electricity Price')

    # Nuclear reference line
    plt.axhline(y=nuclear_ref, color='gray', linestyle='--', linewidth=1)
    plt.text(len(times) - 1.5, nuclear_ref + 10, f'Nuclear Ref ({nuclear_ref} DKK/MWh)', fontsize=8, color='gray', ha='right')

    # Min and max annotations
    min_val = min(prices)
    max_val = max(prices)
    plt.hlines(min_val, 0, prices.index(min_val), colors='blue', linestyles='--', linewidth=1)
    plt.hlines(max_val, 0, prices.index(max_val), colors='red', linestyles='--', linewidth=1)
    plt.text(0, min_val, f'Min: {min_val:.1f}', va='bottom', fontsize=8, color='blue')
    plt.text(0, max_val, f'Max: {max_val:.1f}', va='top', fontsize=8, color='red')

    plt.title(timestamp, fontsize=12)
    plt.xlabel("Time (UTC)", fontsize=10)
    plt.ylabel("Price (DKK/MWh)", fontsize=10)
    plt.xticks(rotation=0, fontsize=8)
    plt.yticks(fontsize=8)
    plt.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, format='jpg', dpi=100)
    else:
        buf = BytesIO()
        plt.savefig(buf, format='jpg', dpi=100)
        buf.seek(0)
        plt.close()
        return buf

    plt.close()



@app.route("/")
def graph_preview():
    buf = generate_plot()
    return send_file(buf, mimetype='image/jpg')

@app.route("/refresh")
def refresh():
    os.makedirs("static", exist_ok=True)
    generate_plot(save_path="static/graph.jpg")
    return "Graph updated!"

@app.route("/image")
def get_image():
    return send_file("static/graph.jpg", mimetype="image/jpg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
