from flask import Flask
import requests
import os

app = Flask(__name__)

@app.route('/')
def index():
    try:
        response = requests.get('https://api.energidataservice.dk/dataset/Elspotprices?limit=5')
        result = response.json()
        records = result.get('records', [])
        html = "<h1>Latest Electricity Prices</h1><ul>"

        for record in records:
            html += f"<li>Price: {record.get('SpotPriceDKK')} DKK/MWh | Time: {record.get('HourDK')}</li>"

        html += "</ul>"
        return html
    except Exception as e:
        return f"<p>Error fetching data: {e}</p>"




if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=True)
