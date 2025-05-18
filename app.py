from flask import Flask, render_template_string
import requests

app = Flask(__name__)

@app.route("/")
def index():
    try:
        response = requests.get("https://api.energidataservice.dk/dataset/Elspotprices?limit=5")
        data = response.json()
        records = data.get("records", [])
    except Exception as e:
        return f"<h1>Error fetching data</h1><p>{e}</p>"

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Electricity Prices</title>
    </head>
    <body>
        <h1>Latest Electricity Prices (Elspot)</h1>
        <ul>
        {% for record in records %}
            <li><strong>{{ record['HourUTC'] }}</strong> - {{ record['PriceArea'] }}: {{ record['SpotPriceDKK'] }} DKK/MWh</li>
        {% endfor %}
        </ul>
    </body>
    </html>
    """
    return render_template_string(html, records=records)

if __name__ == "__main__":
    app.run(debug=True)
