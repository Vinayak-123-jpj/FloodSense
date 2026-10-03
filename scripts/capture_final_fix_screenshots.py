import asyncio
import os
import urllib.request
from playwright.async_api import async_playwright

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

def trigger_demo_alert_api(station_id="KL-PER-02", risk_level="Orange", language="en"):
    url = f"http://127.0.0.1:8000/api/alerts/demo?station_id={station_id}&risk_level={risk_level}&language={language}"
    req = urllib.request.Request(url, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"  [API] Triggered DEMO alert for {station_id}: {resp.status}")
    except Exception as e:
        print(f"  [API Error] {e}")

async def capture():
    print("[Screenshot Script] Launching Playwright Chromium...")
    trigger_demo_alert_api("KL-PER-02", "Orange", "en")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        # 1. Landing Page (Light theme)
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        await page.goto("http://127.0.0.1:8000/?theme=light", wait_until="networkidle")
        await page.wait_for_selector("h1")
        await page.wait_for_timeout(3000)
        p1 = os.path.join(OUTPUT_DIR, "fix_1_5_landing_light.png")
        await page.screenshot(path=p1)
        print(f"  [SAVED] {p1}")

        # 2. Landing Page (Dark theme)
        await page.goto("http://127.0.0.1:8000/?theme=dark", wait_until="networkidle")
        await page.wait_for_selector("h1")
        await page.wait_for_timeout(3000)
        p2 = os.path.join(OUTPUT_DIR, "fix_5_landing_dark.png")
        await page.screenshot(path=p2)
        print(f"  [SAVED] {p2}")

        # 3. Model & Method Page (Light theme)
        await page.goto("http://127.0.0.1:8000/model?theme=light", wait_until="networkidle")
        await page.wait_for_selector("h1")
        await page.wait_for_timeout(3000)
        await page.evaluate("window.scrollTo(0, 1400)")
        await page.wait_for_timeout(1000)
        p3 = os.path.join(OUTPUT_DIR, "fix_2_model_method_table.png")
        await page.screenshot(path=p3)
        print(f"  [SAVED] {p3}")

        # 4. Alerts Page (Showing DEMO alert with Aluva station thresholds)
        await page.goto("http://127.0.0.1:8000/alerts?theme=light", wait_until="networkidle")
        await page.wait_for_selector("h1")
        await page.wait_for_timeout(3000)
        p4 = os.path.join(OUTPUT_DIR, "fix_3_demo_alert_thresholds.png")
        await page.screenshot(path=p4)
        print(f"  [SAVED] {p4}")

        # 5. Scenario Replay Page (Kerala 2018 replay, Thumpamon selected)
        await page.goto("http://127.0.0.1:8000/replay?scenario=kerala_2018&theme=light", wait_until="networkidle")
        await page.wait_for_selector("h1")
        await page.wait_for_timeout(3000)
        p5 = os.path.join(OUTPUT_DIR, "fix_4_replay_thumpamon_no_2018_data.png")
        await page.screenshot(path=p5)
        print(f"  [SAVED] {p5}")

        await browser.close()
        print("[Screenshot Script] All screenshots captured successfully!")

if __name__ == "__main__":
    asyncio.run(capture())
