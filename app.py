from flask import Flask, send_file
import matplotlib.pyplot as plt
import requests
from io import BytesIO
from datetime import datetime
import os

app = Flask(__name__)

def generate_plot(save_path=None, nuclear_ref=300):
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
        plt.savefig(buf, format='png', dpi=100)
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
    generate_plot(save_path="static/graph.png")
    return "Graph updated!"

@app.route("/image")
def get_image():
    return send_file("static/graph.png", mimetype="image/png")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
