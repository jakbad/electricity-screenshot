import asyncio
import os
from flask import Flask, send_file
from pyppeteer import launch
import psutil

app = Flask(__name__)
SCREENSHOT_PATH = os.path.join(os.getcwd(), "screenshot.png")
TARGET_URL = "https://andelenergi.dk/elpriser/"

async def take_screenshot():
    print("🟠 Starting take_screenshot()...")

    mem = psutil.virtual_memory()
    print(f"[Before launching browser] Memory usage: {mem.percent}% used, {mem.available / 1024**2:.1f} MB available")

    try:
        print("🟡 Launching headless browser...")
        browser = await launch(args=["--no-sandbox"])
        page = await browser.newPage()
        await page.goto(TARGET_URL, {'waitUntil': 'networkidle2'})
        await page.screenshot({'path': SCREENSHOT_PATH, 'fullPage': True})
        await browser.close()
        print(f"✅ Screenshot saved to {SCREENSHOT_PATH}")
    except Exception as e:
        print(f"❌ Error taking screenshot: {e}")
        raise

@app.route("/refresh")
def refresh():
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(take_screenshot())
        return "✅ Screenshot refreshed!"
    except Exception as e:
        print(f"❌ Error in /refresh: {e}")
        return f"❌ Error: {e}", 500

@app.route("/image")
def get_image():
    try:
        if os.path.exists(SCREENSHOT_PATH):
            return send_file(SCREENSHOT_PATH, mimetype='image/png')
        else:
            return "❌ Screenshot not found", 404
    except Exception as e:
        print(f"❌ Error in /image: {e}")
        return f"❌ Error: {e}", 500

@app.route("/")
def index():
    return "🎉 Service is live! Use /refresh to take a screenshot and /image to view it."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
