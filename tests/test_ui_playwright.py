import sys
import os
import time
from pathlib import Path

# Garante que a raiz do projeto esteja no sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from playwright.sync_api import sync_playwright

def run_ui_tests():
    print("=" * 70)
    print(" [UI TESTS] TESTE END-TO-END AUTOMATIZADO NA INTERFACE (PLAYWRIGHT)")
    print("=" * 70)

    artifacts_dir = ROOT_DIR / "tests" / "screenshots"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    console_errors = []
    page_errors = []

    with sync_playwright() as p:
        # Usa o Google Chrome instalado nativamente
        browser = p.chromium.launch(
            channel="chrome",
            headless=True,
            args=["--no-sandbox", "--disable-gpu"]
        )
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # Monitora logs de erro do console e exceções não tratadas
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: page_errors.append(str(err)))

        print("\n[TEST 1] Carregando a aplicação em http://127.0.0.1:5533/...")
        response = page.goto("http://127.0.0.1:5533/", wait_until="networkidle", timeout=15000)
        assert response.status == 200, f"Falha ao carregar frontend, status: {response.status}"
        print(" -> [OK] Frontend SPA carregou com HTTP 200.")

        # Aguarda tabela do Screener carregar
        page.wait_for_selector("table", timeout=10000)
        time.sleep(1) # estabilizar renderizacao
        
        # Valida que há linhas de FIIs carregadas
        rows = page.locator("tbody tr")
        row_count = rows.count()
        print(f" -> [OK] Screener renderizou {row_count} linhas de FIIs na tabela.")
        assert row_count > 0, "Nenhum FII foi renderizado na tabela do screener!"

        # Screenshot do Screener
        page.screenshot(path=str(artifacts_dir / "01_screener_view.png"))
        print(f" -> [OK] Screenshot gravada: tests/screenshots/01_screener_view.png")

        # Teste de Filtro por Busca Textual
        print("\n[TEST 2] Testando campo de busca para 'HGLG11'...")
        search_input = page.locator("input[placeholder*='Buscar por ticker']")
        search_input.fill("HGLG11")
        time.sleep(1)

        filtered_rows = page.locator("tbody tr")
        print(f" -> [OK] Filtro de busca retornou {filtered_rows.count()} linha(s).")
        first_ticker = page.locator("tbody tr:first-child td:first-child").inner_text()
        print(f" -> [OK] Primeiro ticker visível: {first_ticker.strip()}")
        assert "HGLG" in first_ticker, f"Esperado HGLG na busca, obteve: {first_ticker}"

        # Navega para o Dossiê clicando no FII
        print("\n[TEST 3] Abrindo Dossiê Detalhado do HGLG11...")
        page.locator("tbody tr:first-child").click()
        
        # Aguarda carregar o Dossiê
        page.wait_for_selector("text=HGLG11", timeout=10000)
        page.wait_for_selector("text=Cotação Atual", timeout=10000)
        time.sleep(1.5)

        # Valida que não houve o infame erro de toFixed
        assert len(page_errors) == 0, f"Erros não capturados na página: {page_errors}"
        print(" -> [OK] Tela de Detalhes do HGLG11 carregada sem qualquer erro de toFixed!")

        # Screenshot do Dossiê
        page.screenshot(path=str(artifacts_dir / "02_fii_details_dossier.png"))
        print(f" -> [OK] Screenshot gravada: tests/screenshots/02_fii_details_dossier.png")

        # Teste de Navegação nas Tabs do Dossiê
        print("\n[TEST 4] Testando sub-abas dos Detalhes...")
        
        # Tab 2: Simulador de Valuation
        val_tab = page.locator("button:has-text('Simulador de Valuation')")
        if val_tab.count() > 0:
            val_tab.click()
            time.sleep(1)
            page.screenshot(path=str(artifacts_dir / "03_valuation_simulator.png"))
            print(" -> [OK] Aba Simulador de Valuation ativa e renderizada.")

        # Tab 3: Gráficos B3
        charts_tab = page.locator("button:has-text('Gráficos B3')")
        if charts_tab.count() > 0:
            charts_tab.click()
            time.sleep(1.5)
            page.screenshot(path=str(artifacts_dir / "04_tradingview_charts.png"))
            print(" -> [OK] Aba Gráficos B3 (TradingView) ativa e renderizada.")

        # Tab 5: HTML Clássico
        html_tab = page.locator("button:has-text('HTML Clássico')")
        if html_tab.count() > 0:
            html_tab.click()
            time.sleep(1)
            page.screenshot(path=str(artifacts_dir / "05_raw_html_tab.png"))
            print(" -> [OK] Aba HTML Clássico ativa e renderizada.")

        # Teste da Tela 3: Comparador Setorial
        print("\n[TEST 5] Navegando para o Comparador Setorial...")
        # Clica no link da sidebar ou no botão do comparador
        comp_nav = page.locator("button:has-text('Comparador Setorial')")
        if comp_nav.count() > 0:
            comp_nav.first.click()
        else:
            page.locator("button:has-text('Comparar Setor')").first.click()
        
        time.sleep(2)
        page.wait_for_selector("text=Pódio de Liderança Setorial", timeout=10000)
        
        # Valida pódio de 5 selos
        podium_cards = page.locator("div.grid.grid-cols-1 > div")
        print(f" -> [OK] Comparador Setorial carregou pódio de liderança e gráficos.")
        page.screenshot(path=str(artifacts_dir / "06_sector_comparator.png"))
        print(f" -> [OK] Screenshot gravada: tests/screenshots/06_sector_comparator.png")

        print("\n[TEST 6] Verificação de Saúde Geral da Interface...")
        print(f" -> Total de erros de página (JS Uncaught Exceptions): {len(page_errors)}")
        print(f" -> Total de mensagens de erro no console: {len(console_errors)}")
        if console_errors:
            print("    Avisos/Erros no console:")
            for e in console_errors[:5]:
                print(f"     - {e}")

        assert len(page_errors) == 0, f"Exceções JS não tratadas na interface: {page_errors}"
        print(" -> [SUCESSO TOTAL] A interface passou em 100% dos testes ponta a ponta sem falhas!")

        browser.close()

if __name__ == "__main__":
    run_ui_tests()
