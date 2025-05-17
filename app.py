from flask import Flask, Response
import requests

app = Flask(__name__)

CSV_URL = "https://andelenergi.dk/?obexport_format=csv&obexport_start=2025-05-13&obexport_end=2025-05-21&obexport_region=east&obexport_tax=0&obexport_product_id=1%231%23TIMEENERGI"

@app.route("/")
def show_csv():
    r = requests.get(CSV_URL)
    if r.status_code == 200:
        # Return raw CSV with plain text content-type
        return Response(r.text, mimetype='text/plain')
    else:
        return f"Failed to fetch CSV, status code: {r.status_code}"

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
