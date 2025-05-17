from flask import Flask, send_file
import asyncio
from pyppeteer import launch
from PIL import Image
import os

app = Flask(__name__)
IMAGE_PATH = "public/electricity.png"
TARGET_URL = "https://andelenergi.dk/el/timepris/"

async def take_screenshot():
    browser = await launch(
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    page = await browser.newPage()
    await page.setViewport({'width': 1200, 'height': 900})
    await page.goto(TARGET_URL, {'waitUntil': 'networkidle2'})
    await asyncio.sleep(5)  # wait for page to load

    # Wait for the canvas price widget to appear
    await page.waitForSelector("canvas", timeout=10000)
    element = await page.querySelector("canvas")
    await element.screenshot({'path': 'screenshot.png'})

    await browser.close()

    os.makedirs("public", exist_ok=True)
    img = Image.open("screenshot.png").convert("L")
    img = img.resize((600, 448), Image.LANCZOS)
    img.save(IMAGE_PATH)
    print(f"Saved screenshot to {IMAGE_PATH}")

def run_screenshot_sync():
    asyncio.run(take_screenshot())

@app.route('/refresh')
def refresh():
    try:
        run_screenshot_sync()
        return "Screenshot refreshed!"
    except Exception as e:
        return f"Failed to refresh screenshot: {e}"

@app.route('/image')
def image():
    if not os.path.exists(IMAGE_PATH):
        return "Image not found. Please visit /refresh first.", 404
    return send_file(IMAGE_PATH, mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
