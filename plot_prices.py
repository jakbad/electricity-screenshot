import requests
import csv
from io import StringIO
import matplotlib.pyplot as plt
from datetime import datetime

CSV_URL = "https://andelenergi.dk/?obexport_format=csv&obexport_start=2025-05-13&obexport_end=2025-05-21&obexport_region=east&obexport_tax=0&obexport_product_id=1%231%23TIMEENERGI"

def download_csv(url=CSV_URL):
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.text

def parse_csv(csv_text):
    f = StringIO(csv_text)
    reader = csv.DictReader(f, delimiter=';')
    times, prices = [], []
    for row in reader:
        dt = datetime.strptime(row['Time'], '%Y-%m-%d %H:%M')
        price = float(row['Price'].replace(',', '.'))
        times.append(dt)
        prices.append(price)
    return times, prices

def plot_prices(times, prices, filename='price_plot.png'):
    plt.figure(figsize=(8,4))
    plt.plot(times, prices, marker='o')
    plt.title("Electricity Prices")
    plt.xlabel("Time")
    plt.ylabel("Price (DKK/kWh)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

if __name__ == "__main__":
    csv_text = download_csv()
    times, prices = parse_csv(csv_text)
    plot_prices(times, prices)
