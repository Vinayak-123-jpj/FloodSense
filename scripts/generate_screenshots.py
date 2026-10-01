"""Automated Screenshot Generator for FloodSense Documentation.

Uses Selenium and Headless Chrome to capture 1440px and 375px screenshots
in both light and dark themes for Landing, Live Monitor, Replay, Alerts, and Model pages.
Saves all 20 screenshots to docs/screenshots/.
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "screenshots")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PAGES = [
    ("landing", "http://localhost:3000/"),
    ("live", "http://localhost:3000/live"),
    ("replay", "http://localhost:3000/replay"),
    ("alerts", "http://localhost:3000/alerts"),
    ("model", "http://localhost:3000/model")
]

VIEWPORTS = [
    ("1440", 1440, 900),
    ("375", 375, 812)
]

THEMES = ["light", "dark"]

def generate_screenshots():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("[Screenshot Script] Initializing browser capture...")
        for page_name, page_url in PAGES:
            for vp_name, width, height in VIEWPORTS:
                for theme in THEMES:
                    print(f"[Screenshot Script] Capturing {page_name} | {vp_name}px | {theme} mode...")
                    driver.set_window_size(width, height)
                    driver.get(page_url)
                    time.sleep(1.5)

                    # Toggle theme in localStorage and document.documentElement class
                    js_code = f"""
                        localStorage.setItem('theme', '{theme}');
                        if ('{theme}' === 'dark') {{
                            document.documentElement.classList.add('dark');
                        }} else {{
                            document.documentElement.classList.remove('dark');
                        }}
                    """
                    driver.execute_script(js_code)
                    time.sleep(1.5) # Wait for Leaflet map tiles and SVG charts to render

                    output_path = os.path.join(OUTPUT_DIR, f"{page_name}_{vp_name}_{theme}.png")
                    driver.save_screenshot(output_path)
                    print(f" Saved: {output_path}")

        print("\n[Screenshot Script] All 20 screenshots successfully captured and saved to docs/screenshots/")
    finally:
        driver.quit()

if __name__ == "__main__":
    generate_screenshots()
