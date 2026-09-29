from playwright.sync_api import sync_playwright
import time
from pathlib import Path

art_path = Path(r"C:\Users\caioc\.gemini\antigravity\brain\bf1569ac-8813-46c8-b6df-a8962ee9991f\screenshots\debt_section_card.png")
art_path.parent.mkdir(parents=True, exist_ok=True)

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1100})
    page.goto("http://127.0.0.1:5173/")
    page.wait_for_selector("table", timeout=10000)
    
    # Search for BTLG11
    search = page.locator("input[placeholder*='Buscar por ticker']")
    search.fill("BTLG11")
    time.sleep(1.5)
    
    # Click on the BTLG11 row to navigate to details
    page.locator("tr:has-text('BTLG11')").first.click()
    page.wait_for_selector("text=Estrutura de Capital", timeout=15000)
    time.sleep(2)
    
    # Scroll to the debt section
    elem = page.locator("text=Estrutura de Capital").first
    elem.scroll_into_view_if_needed()
    time.sleep(1)
    
    page.screenshot(path=str(art_path))
    browser.close()
    print("Screenshot saved to:", art_path)
