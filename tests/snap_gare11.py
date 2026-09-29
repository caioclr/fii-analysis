from playwright.sync_api import sync_playwright
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
out_path = ROOT / "tests" / "screenshots" / "gare11_fixed.png"
art_path = Path(r"C:\Users\caioc\.gemini\antigravity\brain\bf1569ac-8813-46c8-b6df-a8962ee9991f\screenshots\gare11_fixed.png")

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://127.0.0.1:5173/")
    page.wait_for_selector("table", timeout=10000)
    search = page.locator("input[placeholder*='Buscar por ticker']")
    search.fill("gare1")
    time.sleep(1.5)
    page.screenshot(path=str(out_path))
    page.screenshot(path=str(art_path))
    browser.close()
    print("Captura concluida com sucesso!")
