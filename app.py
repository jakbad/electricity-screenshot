from flask import Flask, send_file
import matplotlib.pyplot as plt
import requests
from io import BytesIO
from datetime import datetime, timedelta
import os

app = Flask(__name__)

import requests
from datetime import datetime
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def generate_plot(save_path=None, nuclear_ref=300):
    url = "https://api.energidataservice.dk/dataset/Elspotprices?limit=48&filter={\"PriceArea\":\"DK2\"}&sort=HourUTC DESC"
    response = requests.get(url)
    data = response.json().get("records", [])

    data.sort(key=lambda x: x["HourUTC"])  # Ascending

    times_raw = [datetime.fromisoformat(rec["HourUTC"]) for rec in data]
    prices = [rec["SpotPriceDKK"] for rec in data]

    timestamp = datetime.now().strftime("Prices as of: %Y-%m-%d %H:%M")

    fig, ax = plt.subplots(figsize=(6, 4.48), dpi=100)
    ax.plot(times_raw, prices, marker='o', linestyle='-', color='black', label='Electricity Price')

    # Nuclear reference line
    ax.axhline(y=nuclear_ref, color='gray', linestyle='--', linewidth=1)
    ax.text(times_raw[-2], nuclear_ref + 10, f'Nuclear Ref ({nuclear_ref} DKK/MWh)', fontsize=8, color='gray', ha='right')

    # Min/max annotations
    min_idx = prices.index(min(prices))
    max_idx = prices.index(max(prices))
    ax.hlines(prices[min_idx], xmin=times_raw[0], xmax=times_raw[min_idx], colors='blue', linestyles='--', linewidth=1)
    ax.hlines(prices[max_idx], xmin=times_raw[0], xmax=times_raw[max_idx], colors='red', linestyles='--', linewidth=1)
    ax.text(times_raw[0], prices[min_idx], f'Min: {prices[min_idx]:.1f}', va='bottom', fontsize=8, color='blue')
    ax.text(times_raw[0], prices[max_idx], f'Max: {prices[max_idx]:.1f}', va='top', fontsize=8, color='red')

    # X-axis formatting
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))  # Every hour
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H'))    # Hour only

    # Add vertical lines at date changes
    previous_date = times_raw[0].date()
    for i, t in enumerate(times_raw):
        if t.date() != previous_date:
            ax.axvline(x=t, color='gray', linestyle=':', linewidth=0.8)
            ax.text(t, ax.get_ylim()[0], t.strftime('%d/%m'), fontsize=8,
                    rotation=90, va='bottom', ha='right', color='gray', clip_on=True)
            previous_date = t.date()

    plt.title(timestamp, fontsize=12)
    plt.xlabel("Hour", fontsize=10)
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
