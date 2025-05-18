from flask import Flask, render_template_string, send_file
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io

app = Flask(__name__)

API_URL = "https://api.energidataservice.dk/dataset/Elspotprices?limit=24&filter={%22PriceArea%22:%22DK2%22}"

def fetch_elspot_data():
    response = requests.get(API_URL)
    data = response.json()
    return data.get("records", [])

@app.route("/")
def index():
    records = fetch_elspot_data()
    prices = [
        f"{rec['SpotPriceDKK']} DKK/MWh | Time: {rec['HourUTC']}"
        for rec in records
    ]
    html = """
    <h1>Latest Electricity Prices</h1>
    <ul>
        {% for price in prices %}
            <li>{{ price }}</li>
        {% endfor %}
    </ul>
    <p><a href="/image">View Graph</a></p>
    """
    return render_template_string(html, prices=prices)

def create_price_plot(records):
    # Parse times and prices
    times = [datetime.fromisoformat(rec["HourUTC"]) for rec in records]
    prices = [rec["SpotPriceDKK"] for rec in records]

    # Create the plot
    fig, ax = plt.subplots(figsize=(6,
