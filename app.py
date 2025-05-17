import asyncio
import os
from flask import Flask, send_file
from pyppeteer import launch
from PIL import Image

app = Flask(__name__)
TARGET_URL = "https://andelenergi.dk"  # Change to specific page if needed
IMAGE_PATH = "public/electricity.png"

async def take_screenshot():
    print("Taking screenshot...")
    browser = await launch(
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    page = await browser.newPage()
    await page.setViewport({'width': 1200, 'height': 900})
    await page.goto(TARGET_URL)
    await asyncio.sleep(5)
    await page.screenshot({'path': 'screenshot.png'})
    await browser.close()

    img = Image.open("screenshot.png").convert("L")  # Grayscale
    img = img.resize((600, 448), Image.LANCZOS)
    os.makedirs("public", exist_ok=True)
    img.save(IMAGE_PATH)
    print("Screenshot saved and resized.")

@app.route("/")
def home():
    return "<h2>Electricity Screenshot Service</h2><p>Visit <code>/image</code> to view.</p>"

@app.route("/refresh")
def refresh_image():
    asyncio.get_event_loop().run_until_complete(take_screenshot())
    return "Screenshot refreshed!"

@app.route("/image")
def serve_image():
    if os.path.exists(IMAGE_PATH):
        return send_file(IMAGE_PATH, mimetype="image/png")
    else:
        return "Image not found. Please visit /refresh first.", 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
