from flask import Flask, Response, request
import io
import requests
import pandas as pd
import matplotlib.pyplot as plt

app = Flask(__name__)

CSV_URL_TEMPLATE = (
    "https://andelenergi.dk/?obexport_format=csv"
    "&obexport_start={start_date}"
    "&obexport_end={end_date}"
    "&obexport_region=east"
    "&obexport_tax=0"
    "&obexport_product_id=1%231%23TIMEENERGI"
)

def fetch_and_parse_csv(start_date, end_date):
    url = CSV_URL_TEMPLATE.format(start_date=start_date, end_date=end_date)
    resp = requests.get(url)
    resp.raise_for_status()
    # CSV uses semicolon delimiter, Danish locale decimal comma replaced by dot
    df = pd.read_csv(io.StringIO(resp.text), delimiter=';')
    # Convert price column to numeric, assuming column named "Price" or similar
    # Inspect CSV headers and adjust column name accordingly
    # For example, it might be "TimePrice" or "Pris"
    # Here we guess "Price" or fallback
    price_col = None
    for col in df.columns:
        if "pris" in col.lower() or "price" in col.lower():
            price_col = col
            break
    if price_col is None:
        raise ValueError("Price column not found in CSV")

    # Replace comma decimal separator if present and convert to float
    df[price_col] = df[price_col].astype(str).str.replace(",", ".").astype(float)

    # Parse datetime from first column (adjust name if needed)
    df[df.columns[0]] = pd.to_datetime(df[df.columns[0]], dayfirst=True, errors='coerce')

    return df[[df.columns[0], price_col]].dropna()

@app.route("/plot")
def plot_prices():
    # Allow date range as query parameters, else default last 7 days
    start_date = request.args.get("start", None)
    end_date = request.args.get("end", None)
    if not start_date or not end_date:
        import datetime
        today = datetime.date.today()
        start_date = (today - datetime.timedelta(days=7)).isoformat()
        end_date = today.isoformat()

    try:
        df = fetch_and_parse_csv(start_date, end_date)
    except Exception as e:
        return f"Failed to fetch or parse CSV: {e}", 500

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df[df.columns[0]], df[df.columns[1]], marker="o", linestyle="-")
    ax.set_title(f"Electricity Prices {start_date} to {end_date}")
    ax.set_xlabel("Date and Time")
    ax.set_ylabel("Price (DKK/kWh)")
    plt.xticks(rotation=45)
    plt.tight_layout()

    img_bytes = io.BytesIO()
    plt.savefig(img_bytes, format="png")
    plt.close(fig)
    img_bytes.seek(0)

    return Response(img_bytes.getvalue(), mimetype="image/png")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
