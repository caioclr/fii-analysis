import unittest
import os
import sys
import re
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

from src.services.market_data import MarketDataService
from src.services.cross_validation_service import CrossValidationService
from src.services.report_generator import ReportGenerator

class TestDataValidation(unittest.TestCase):
    """
    Bateria de testes automatizada para validação de dados, reconciliação contábil vs mercado,
    cálculo de liquidez (ADTV) e garantia de preenchimento completo de dossiês HTML.
    """

    @classmethod
    def setUpClass(cls):
        cls.root_dir = Path(__file__).resolve().parent.parent
        cls.docs_dir = cls.root_dir / "docs"

    def test_01_documentation_integrity(self):
        """Verifica se todos os 6 documentos oficiais existem, têm tamanho adequado e sem caracteres corrompidos."""
        doc_files = [
            "README.md",
            "01_visao_funcional.md",
            "02_fluxos_de_informacao.md",
            "03_setores_e_metricas.md",
            "04_guia_de_uso.md",
            "05_governanca_e_validacao_de_dados.md"
        ]
        
        control_chars = [chr(i) for i in list(range(0, 9)) + [11, 12] + list(range(14, 32))]

        for doc_name in doc_files:
            file_path = self.docs_dir / doc_name
            self.assertTrue(file_path.exists(), f"Documento ausente: {doc_name}")
            
            size = file_path.stat().st_size
            self.assertGreater(size, 1000, f"Documento {doc_name} muito pequeno ({size} bytes)")
            
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                for c in control_chars:
                    self.assertNotIn(c, content, f"Caractere de controle inválido (hex {ord(c):02x}) em {doc_name}")
        
        print(" -> [OK] 100% da documentação oficial validada (6 arquivos íntegros).")

    def test_02_rbry11_market_quote_and_adtv(self):
        """Valida que o RBRY11 busca a cotação real de mercado na B3 e possui ADTV consistente."""
        data = MarketDataService.get_market_data("RBRY11")
        
        price = data.get("current_price")
        self.assertIsNotNone(price, "Cotação do RBRY11 não pode ser nula")
        self.assertGreater(price, 0.0, f"Cotação do RBRY11 deve ser positiva: {price}")
        
        # O preço de mercado deve ser um valor razoável do pregão B3 (ex: entre 50 e 150)
        self.assertTrue(50.0 <= price <= 150.0, f"Cotação de mercado atípica para RBRY11: R$ {price}")
        
        # O ADTV deve estar preenchido e ser positivo
        adtv = data.get("adtv_milhoes")
        self.assertIsNotNone(adtv, "ADTV em milhões do RBRY11 não pode ser nulo")
        self.assertGreater(adtv, 0.0, f"ADTV do RBRY11 deve ser maior que zero: {adtv}")

        print(f" -> [OK] RBRY11 validado: Preço B3 = R$ {price:.2f} | ADTV = R$ {adtv:.2f} mi/dia")

    def test_03_vilg11_and_btci11_market_data(self):
        """Valida a resolução de cotação e ADTV para VILG11 (Logística) e BTCI11 (Papel)."""
        for ticker in ["VILG11", "BTCI11"]:
            data = MarketDataService.get_market_data(ticker)
            price = data.get("current_price")
            adtv = data.get("adtv_milhoes")
            
            self.assertIsNotNone(price, f"Preço de {ticker} não pode ser nulo")
            self.assertGreater(price, 0.0, f"Preço de {ticker} deve ser > 0")
            self.assertIsNotNone(adtv, f"ADTV de {ticker} não pode ser nulo")
            self.assertGreater(adtv, 0.0, f"ADTV de {ticker} deve ser > 0")
            
            print(f" -> [OK] {ticker} validado: Preço = R$ {price:.2f} | ADTV = R$ {adtv:.2f} mi/dia")

    def test_04_vilg11_html_no_dark_donuts_and_no_empty_tables(self):
        """
        Valida que o relatório HTML de VILG11 possui:
        1. Comprimento substancial (> 25.000 caracteres)
        2. Ausência de 'background: #334155;' (donuts escuros desconfigurados)
        3. Ausência de tabelas com '<tbody></tbody>' vazias
        4. Presença das seções vitais: DRE Caixa, Galpões, Inquilinos e Vencimentos.
        """
        res = ReportGenerator.generate_html_report("VILG11")
        self.assertEqual(res.get("ticker"), "VILG11")
        self.assertEqual(res.get("segment_code"), "LOGISTICA")
        
        html = res.get("html_content", "")
        self.assertGreater(len(html), 25000, f"HTML de VILG11 muito curto: {len(html)} caracteres")
        
        # Teste crítico 1: Ausência de donut escuro unrendered
        self.assertNotIn(
            "background: #334155;",
            html,
            "Detectado donut unrendered com estilo estático 'background: #334155;' no HTML de VILG11!"
        )
        
        # Teste crítico 2: Ausência de tbody vazio
        clean_html = re.sub(r"\s+", "", html)
        self.assertNotIn(
            "<tbody></tbody>",
            clean_html,
            "Detectada tabela vazia com '<tbody></tbody>' sem linhas no HTML de VILG11!"
        )
        
        # Teste de seções vitais
        self.assertIn("DRE", html, "Seção DRE ausente no HTML")
        self.assertIn("Alocação de Ativos", html, "Seção de Alocação ausente no HTML")
        self.assertIn("Engenharia", html, "Seção de Engenharia/Condomínios ausente no HTML")
        self.assertIn("Locatários", html, "Seção de Inquilinos ausente no HTML")
        self.assertIn("Alavancagem Financeira", html, "Seção de Alavancagem ausente no HTML")
        self.assertIn("Matriz Crítica", html, "Seção de Flags ausente no HTML")
        self.assertIn("conic-gradient(", html, "Gráficos de rosca pure CSS ausentes no HTML")

        print(f" -> [OK] VILG11 HTML auditado: {len(html):,} bytes, 0 donuts escuros e 0 tabelas vazias.")

    def test_05_rbry11_and_btci11_papel_html_integrity(self):
        """Valida a integridade dos dossiês HTML dos fundos de Papel/CRI RBRY11 e BTCI11."""
        for ticker in ["RBRY11", "BTCI11"]:
            res = ReportGenerator.generate_html_report(ticker)
            self.assertEqual(res.get("ticker"), ticker)
            self.assertEqual(res.get("segment_code"), "PAPEL")
            
            html = res.get("html_content", "")
            self.assertGreater(len(html), 25000, f"HTML de {ticker} muito curto: {len(html)} caracteres")
            
            self.assertNotIn("background: #334155;", html, f"Donut unrendered encontrado no HTML de {ticker}")
            
            clean_html = re.sub(r"\s+", "", html)
            self.assertNotIn("<tbody></tbody>", clean_html, f"Tabela vazia encontrada no HTML de {ticker}")
            
            self.assertIn("DRE de Crédito", html)
            self.assertIn("Indexadores", html)
            self.assertIn("Maiores Devedores", html)
            self.assertIn("Curva de Juros", html)
            self.assertIn("conic-gradient(", html)
            
            print(f" -> [OK] {ticker} (Papel) HTML auditado: {len(html):,} bytes íntegros.")

    def test_06_shopping_xpml11_html_integrity(self):
        """Valida o dossiê especializado de Shoppings (XPML11)."""
        res = ReportGenerator.generate_html_report("XPML11")
        self.assertEqual(res.get("ticker"), "XPML11")
        self.assertEqual(res.get("segment_code"), "SHOPPING")
        
        html = res.get("html_content", "")
        self.assertGreater(len(html), 25000)
        self.assertNotIn("background: #334155;", html)
        
        clean_html = re.sub(r"\s+", "", html)
        self.assertNotIn("<tbody></tbody>", clean_html)
        
        self.assertIn("DRE", html)
        self.assertIn("Shopping", html)
        self.assertIn("Locatários", html)
        self.assertIn("conic-gradient(", html)
        
        print(f" -> [OK] XPML11 (Shoppings) HTML auditado: {len(html):,} bytes íntegros.")

    def test_07_cross_validation_spread_calculations(self):
        """Valida que o CrossValidationService calcula spreads e indicadores macro sem erros matemáticos."""
        for ticker in ["RBRY11", "VILG11", "XPML11"]:
            cross = CrossValidationService.validate_and_reconcile(ticker)
            self.assertEqual(cross.get("ticker"), ticker)
            
            reconcil = cross.get("reconciliation", {})
            self.assertTrue(reconcil.get("validated"), f"Validação cruzada falhou para {ticker}")
            
            bolsai = cross.get("bolsai", {})
            macro = bolsai.get("macro", {})
            
            # Checa se os spreads são números válidos
            self.assertIsInstance(macro.get("spread_vs_cdi"), (int, float))
            self.assertIsInstance(macro.get("spread_vs_ipca"), (int, float))
            self.assertIn("spread_status", macro)
            
            # Checa se a desagregação contábil fnet existe
            fnet = cross.get("fnet", {})
            self.assertIn("vpc", fnet)
            self.assertIn("pl", fnet)
            
            print(f" -> [OK] Validação cruzada {ticker}: Spread vs CDI = {macro.get('spread_vs_cdi'):+.2f}% | Validado: Sim")

if __name__ == "__main__":
    print("=" * 70)
    print(" [TESTES] INICIANDO BATERIA DE INTEGRIDADE E VALIDACAO DE DADOS")
    print("=" * 70)
    unittest.main(verbosity=2)
