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
    ax.plot(times_raw, prices, marker='o', linestyle='-', color='black')

    # Nuclear reference line
    ax.axhline(y=nuclear_ref, color='gray', linestyle='--', linewidth=1)
    ax.text(times_raw[-2], nuclear_ref + 10, f'Nuclear Ref ({nuclear_ref} DKK/MWh)', fontsize=8, color='gray', ha='right')

    # Min/max lines
    min_val = min(prices)
    max_val = max(prices)
    min_idx = prices.index(min_val)
    max_idx = prices.index(max_val)
    ax.hlines(min_val, xmin=times_raw[0], xmax=times_raw[min_idx], colors='blue', linestyles='--', linewidth=1)
    ax.hlines(max_val, xmin=times_raw[0], xmax=times_raw[max_idx], colors='red', linestyles='--', linewidth=1)
    ax.text(times_raw[0], min_val, f'Min: {min_val:.1f}', va='bottom', fontsize=8, color='blue')
    ax.text(times_raw[0], max_val, f'Max: {max_val:.1f}', va='top', fontsize=8, color='red')

    # X-axis: show only hour (HH)
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H'))

    # Add vertical lines and date labels on date change
    previous_date = times_raw[0].date()
    for t in times_raw:
        if t.date() != previous_date:
            ax.axvline(x=t, color='gray', linestyle=':', linewidth=0.8)
            ax.text(t, ax.get_ylim()[0], t.strftime('%d/%m'), fontsize=8,
                    rotation=90, va='bottom', ha='center', color='gray', clip_on=True)
            previous_date = t.date()

    ax.set_title(timestamp, fontsize=12)
    ax.set_xlabel("Hour (UTC)", fontsize=10)
    ax.set_ylabel("Price (DKK/MWh)", fontsize=10)
    ax.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='y', labelsize=8)
    ax.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    fig.tight_layout()

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
