from flask import Flask, send_file
import asyncio
import nest_asyncio  # <--- NEW
from pyppeteer import launch
from PIL import Image
import os
import psutil
nest_asyncio.apply()  # <--- NEW

app = Flask(__name__)
IMAGE_PATH = "public/electricity.png"
TARGET_URL = "https://andelenergi.dk/el/timepris/"



def log_memory_usage(stage=""):
    mem = psutil.virtual_memory()
    print(f"[{stage}] Memory usage: {mem.percent}% used, {mem.available / 1024 ** 2:.1f} MB available")

async def take_screenshot():
    try:
        print("🟠 Starting take_screenshot()...")
        log_memory_usage("Before launching browser")

        browser = await launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--single-process',
                '--no-zygote',
            ]
        )
        log_memory_usage("After launching browser")

        page = await browser.newPage()
        await page.setViewport({'width': 1280, 'height': 1024})
        print("🟡 Navigating to URL...")
        await page.goto('https://andelenergi.dk/el/timepris/', {'waitUntil': 'networkidle2'})
        await asyncio.sleep(5)  # Allow time for rendering

        print("📸 Taking screenshot...")
        await page.screenshot({'path': 'screenshot.png', 'fullPage': True})

        await browser.close()
        print("✅ Screenshot saved as screenshot.png")
    except Exception as e:
        print(f"❌ Failed to take screenshot: {e}")


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
