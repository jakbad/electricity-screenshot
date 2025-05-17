import asyncio
import os
import concurrent.futures
from flask import Flask, send_file
from pyppeteer import launch
from PIL import Image

app = Flask(__name__)
TARGET_URL = "https://andelenergi.dk"
IMAGE_PATH = "public/electricity.png"

executor = concurrent.futures.ThreadPoolExecutor()

async def take_screenshot():
    try:
        print("Starting browser...")
        browser = await launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        page = await browser.newPage()
        await page.setViewport({'width': 1200, 'height': 900})
        print(f"Loading page {TARGET_URL} ...")
        await page.goto(TARGET_URL)
        await asyncio.sleep(5)  # wait for page to load

        print("Taking screenshot...")
        await page.screenshot({'path': 'screenshot.png'})
        await browser.close()

        print("Resizing image...")
        os.makedirs("public", exist_ok=True)
        img = Image.open("screenshot.png").convert("L")  # grayscale
        img = img.resize((600, 448), Image.LANCZOS)
        img.save(IMAGE_PATH)
        print("Image saved.")
    except Exception as e:
        print(f"Error during screenshot: {e}")
        raise

@app.route("/")
def home():
    return "<h2>Electricity Screenshot Service</h2><p>Use /refresh to update image, /image to view.</p>"

@app.route("/refresh")
def refresh_image():
    try:
        future = executor.submit(lambda: asyncio.run(take_screenshot()))
        future.result()  # wait for it to finish
        return "Screenshot refreshed!"
    except Exception as e:
        return f"Failed to refresh screenshot: {e}", 500

@app.route("/image")
def serve_image():
    if os.path.exists(IMAGE_PATH):
        return send_file(IMAGE_PATH, mimetype="image/png")
    else:
        return "Image not found. Please visit /refresh first.", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
