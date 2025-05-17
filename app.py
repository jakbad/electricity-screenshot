import os
import concurrent.futures
from flask import Flask, send_file

app = Flask(__name__)
TARGET_URL = "https://andelenergi.dk"
IMAGE_PATH = "public/electricity.png"

# Create a process pool to run screenshot code in a separate process
executor = concurrent.futures.ProcessPoolExecutor()

async def take_screenshot():
    from pyppeteer import launch
    from PIL import Image
    import os
    import asyncio

    browser = await launch(
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    page = await browser.newPage()
    await page.setViewport({'width': 1200, 'height': 900})

    TARGET_URL = "https://andelenergi.dk/el/timepris/"
    await page.goto(TARGET_URL, {'waitUntil': 'networkidle2'})
    await asyncio.sleep(5)

    # Optionally accept cookie banner here (see earlier cookie handling)
    # ...

    await page.waitForSelector("canvas", timeout=10000)
    element = await page.querySelector("canvas")
    await element.screenshot({'path': 'screenshot.png'})

    await browser.close()

    os.makedirs("public", exist_ok=True)
    img = Image.open("screenshot.png").convert("L")
    img = img.resize((600, 448), Image.LANCZOS)
    img.save("public/electricity.png")
    print("Saved screenshot to public/electricity.png")


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
