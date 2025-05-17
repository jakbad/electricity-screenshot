from flask import Flask, send_file
import asyncio
import nest_asyncio  # <--- NEW
from pyppeteer import launch
from PIL import Image
import os

nest_asyncio.apply()  # <--- NEW

app = Flask(__name__)
IMAGE_PATH = "public/electricity.png"
TARGET_URL = "https://andelenergi.dk/el/timepris/"

async def take_screenshot():
    print("🟡 Launching headless browser...")
    browser = await launch(
        headless=True,
        args=['--no-sandbox', '--disable-setuid-sandbox']
    )
    page = await browser.newPage()
    await page.setViewport({'width': 1200, 'height': 900})

    print("🟡 Navigating to page:", TARGET_URL)
    await page.goto(TARGET_URL, {'waitUntil': 'networkidle2'})
    await asyncio.sleep(5)  # Give extra time for JS and widgets

    try:
        print("🟡 Waiting for canvas element...")
        await page.waitForSelector("canvas", timeout=10000)
        element = await page.querySelector("canvas")
        if element:
            print("🟢 Canvas element found. Taking screenshot...")
            await element.screenshot({'path': 'screenshot.png'})
            print("✅ Screenshot saved to screenshot.png")
        else:
            print("❌ Canvas element not found.")
    except Exception as e:
        print(f"❌ Error during canvas screenshot: {e}")
        await browser.close()
        return

    await browser.close()
    print("🟢 Browser closed.")

    try:
        exists = os.path.exists("screenshot.png")
        print("📷 Screenshot file exists:", exists)

        os.makedirs("public", exist_ok=True)

        if exists:
            img = Image.open("screenshot.png").convert("L")
            img = img.resize((600, 448), Image.LANCZOS)
            img.save(IMAGE_PATH)
            print(f"✅ Processed and saved image to {IMAGE_PATH}")
        else:
            print("❌ screenshot.png does not exist. Aborting image processing.")
    except Exception as e:
        print(f"❌ Failed to process or save screenshot: {e}")


def run_screenshot_sync():
    return asyncio.get_event_loop().run_until_complete(take_screenshot())

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
