from playwright.sync_api import sync_playwright
import time
from pathlib import Path

art_path = Path(r"C:\Users\caioc\.gemini\antigravity\brain\bf1569ac-8813-46c8-b6df-a8962ee9991f\screenshots\scores_unified.png")
art_path.parent.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://127.0.0.1:5173/")
    page.wait_for_selector("table", timeout=10000)
    page.click("text=Shoppings")
    time.sleep(2)
    page.screenshot(path=str(art_path))
    browser.close()
    print("Captura salva em:", art_path)
