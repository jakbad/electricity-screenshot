import os
import concurrent.futures
from flask import Flask, send_file

app = Flask(__name__)
TARGET_URL = "https://andelenergi.dk/el/timepris/"
IMAGE_PATH = "public/electricity.png"

# Create a process pool to run screenshot code in a separate process
executor = concurrent.futures.ProcessPoolExecutor()

def run_screenshot_sync():
    import asyncio
    from pyppeteer import launch
    from PIL import Image

async def take_screenshot():
    print("Launching browser...")
    browser = await launch(
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    page = await browser.newPage()
    await page.setViewport({'width': 1200, 'height': 900})
    print(f"Opening {TARGET_URL} ...")
    await page.goto(TARGET_URL)
    await asyncio.sleep(3)

    # Try to click cookie accept button if it exists
    try:
        await page.waitForSelector("button#onetrust-accept-btn-handler", timeout=5000)
        print("Cookie banner detected. Accepting...")
        await page.click("button#onetrust-accept-btn-handler")
        await asyncio.sleep(1)
    except Exception:
        print("No cookie banner found or already accepted.")

    print("Taking screenshot...")
    await page.screenshot({'path': 'screenshot.png'})
    await browser.close()

    print("Processing image...")
    os.makedirs("public", exist_ok=True)
    img = Image.open("screenshot.png").convert("L")
    img = img.resize((600, 448), Image.LANCZOS)
    img.save(IMAGE_PATH)
    print("Image saved to:", IMAGE_PATH)


    asyncio.run(take_screenshot())

@app.route("/")
def home():
    return "<h2>Electricity Screenshot Service</h2><p>Use /refresh to update image, /image to view.</p>"

@app.route("/refresh")
def refresh_image():
    try:
        future = executor.submit(run_screenshot_sync)
        future.result()
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
