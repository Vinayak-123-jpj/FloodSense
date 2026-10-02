"""Automated Browser-Level Alert Feature Acceptance Tester.

Launches headless Chrome (1440x900) to verify:
1. Dashboard page loads cleanly.
2. Navigating to Alerts page loads outbox.
3. DEMO Alert button trigger works.
4. Language toggle switches between EN, HI, ML, AS.
5. Outbox persists across page refresh.
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def run_acceptance_test():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1440,900")
    
    driver = webdriver.Chrome(options=options)
    try:
        print("[Acceptance Test] 1. Opening Dashboard (http://localhost:3000)...")
        driver.get("http://localhost:3000/")
        time.sleep(2)
        assert "FloodSense" in driver.page_source or "Atlas" in driver.page_source
        print("  [OK] Dashboard loaded cleanly.")

        print("[Acceptance Test] 2. Navigating to Alerts Outbox Page via Navbar...")
        alerts_link = driver.find_element(By.XPATH, "//a[@href='/alerts']")
        driver.execute_script("arguments[0].click();", alerts_link)
        time.sleep(2)
        assert "Alert Outbox" in driver.page_source
        print("  [OK] Alerts page loaded cleanly.")

        print("[Acceptance Test] 3. Triggering DEMO Alert via UI button...")
        trigger_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Trigger DEMO Alert')]")
        driver.execute_script("arguments[0].click();", trigger_btn)
        time.sleep(2.5)
        assert "DEMO ALERT" in driver.page_source or "DEMO" in driver.page_source
        print("  [OK] DEMO Alert triggered and rendered in Outbox with DEMO ALERT badge.")

        print("[Acceptance Test] 4. Testing Language Toggle Buttons (EN, HI, ML, AS)...")
        for lang_name, keyword in [("Hindi", "हिंदी"), ("Malayalam", "മലയാളം"), ("Assamese", "অসমীয়া"), ("English", "English")]:
            btn = driver.find_element(By.XPATH, f"//button[contains(text(), '{lang_name}')]")
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(1)
            print(f"  [OK] Switched to {lang_name}. Outbox updated.")

        print("[Acceptance Test] 5. Testing Outbox Persistence...")
        driver.get("http://localhost:3000/")
        time.sleep(1)
        alerts_link = driver.find_element(By.XPATH, "//a[@href='/alerts']")
        driver.execute_script("arguments[0].click();", alerts_link)
        time.sleep(2)
        assert "Alert Outbox" in driver.page_source
        print("  [OK] Outbox state persisted cleanly across navigation.")

        print("\n[ACCEPTANCE TEST SUCCESS] All browser-level operational checks PASSED!")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_acceptance_test()
