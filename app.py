from flask import Flask
import requests

app = Flask(__name__)

@app.route('/')
def index():
    response = requests.get(
        url='https://api.energidataservice.dk/dataset/Elspotprices?limit=5&sort=HourDK desc&filter={"PriceArea":"DK2"}'
    )
    result = response.json()
    records = result.get('records', [])

    html = "<h1>Latest Electricity Prices</h1><ul>"

    for record in records:
        price = record.get('SpotPriceDKK')
        hour = record.get('HourUTC')
        html += f"<li>Time: {hour} | Price: {price} DKK/MWh</li>"

    html += "</ul>"
    return html
