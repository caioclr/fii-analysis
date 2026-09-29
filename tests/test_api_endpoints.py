import unittest
import sys
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

from fastapi.testclient import TestClient
from src.api.main import app

class TestApiEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_healthcheck(self):
        """Valida que o endpoint de healthcheck da API responde com sucesso."""
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("status"), "healthy")
        print(" -> [OK] Healthcheck endpoint ativo.")

    def test_02_pricing_parameters(self):
        """Valida a consulta dos parâmetros macroeconômicos padrão."""
        resp = self.client.get("/api/settings/pricing-parameters")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("ntnb_reference_rate", data)
        self.assertIn("projected_ipca", data)
        self.assertIn("real_risk_spread", data)
        print(f" -> [OK] Parâmetros macro: NTN-B {data['ntnb_reference_rate']}% | IPCA {data['projected_ipca']}%")

    def test_03_fii_screener(self):
        """Valida a listagem de FIIs no screener com suporte a paginação."""
        resp = self.client.get("/api/fii/screener?limit=20")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreater(data.get("total", 0), 0)
        self.assertGreater(len(data.get("items", [])), 0)
        self.assertIn("LOGISTICA", data.get("segments", []))
        first_item = data["items"][0]
        self.assertIn("ticker", first_item)
        self.assertIn("close_price", first_item)
        print(f" -> [OK] Screener retornou {data['total']} FIIs catalogados ({len(data['items'])} exibidos).")

    def test_04_fii_screener_filter_segment(self):
        """Valida o filtro de segmento (ex: LOGISTICA) no screener."""
        resp = self.client.get("/api/fii/screener?segment=LOGISTICA&limit=50")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        items = data.get("items", [])
        self.assertGreater(len(items), 0)
        for it in items:
            self.assertEqual(it["segment_code"], "LOGISTICA")
        print(f" -> [OK] Filtro de segmento 'LOGISTICA' retornou {len(items)} fundos válidos.")

    def test_05_fii_details_100_percent_data(self):
        """Valida que o endpoint de detalhes retorna 100% dos dados estruturados e o raw_html."""
        for ticker in ["HGLG11", "RBRY11"]:
            resp = self.client.get(f"/api/fii/{ticker}/details")
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            
            # Header
            header = data.get("header", {})
            self.assertEqual(header.get("ticker"), ticker)
            self.assertIn("score", header)
            self.assertIn("veredicto", header)
            
            # KPIs
            kpis = data.get("kpis", {})
            self.assertGreater(kpis.get("preco_mercado", 0), 0)
            self.assertGreater(kpis.get("vpc", 0), 0)
            self.assertGreater(kpis.get("adtv_milhoes", 0), 0)
            
            # DRE Caixa
            dre = data.get("dre", {})
            self.assertGreater(len(dre.get("linhas", [])), 0)
            self.assertIn("ffo_cota", dre)
            
            # Ativos & Inquilinos
            self.assertGreater(len(data.get("ativos", [])), 0)
            self.assertGreater(len(data.get("inquilinos", [])), 0)
            
            # Flags
            self.assertGreater(len(data.get("green_flags", [])), 0)
            
            # Parecer & Raw HTML
            parecer = data.get("parecer", {})
            self.assertIn("conclusao", parecer)
            self.assertGreater(len(data.get("raw_html", "")), 20000)
            
            print(f" -> [OK] Detalhes de {ticker}: 100% dos dados estruturados e HTML ({len(data['raw_html']):,} bytes).")

    def test_06_fii_market_series(self):
        """Valida que as séries temporais B3 estão formatadas para o TradingView Lightweight Charts."""
        resp = self.client.get("/api/fii/HGLG11/market-series?period=1mo")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("ticker"), "HGLG11")
        series = data.get("series", [])
        self.assertGreater(len(series), 0)
        pt = series[-1]
        self.assertIn("time", pt)
        self.assertIn("open", pt)
        self.assertIn("close", pt)
        self.assertIn("volume", pt)
        print(f" -> [OK] TradingView market-series: {len(series)} candles diários retornados.")

    def test_07_fii_valuation_simulate(self):
        """Valida a simulação de valuation com parâmetros dinâmicos."""
        payload = {
            "ntnb_reference_rate": 7.00,
            "projected_ipca": 4.50,
            "real_risk_spread": 2.50,
            "ke": 0.12,
            "g_growth": 0.045
        }
        resp = self.client.post("/api/fii/HGLG11/valuation-simulate", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("ticker"), "HGLG11")
        self.assertGreater(data.get("preco_teto_recomendado", 0), 0)
        self.assertIn("margem_seguranca_pct", data)
        self.assertIn("metodologias", data)
        print(f" -> [OK] Simulação de Valuation HGLG11: Preço-Teto = R$ {data['preco_teto_recomendado']:.2f} | Margem = {data['margem_seguranca_pct']:+.1f}%")

    def test_08_fii_compare_sector(self):
        """Valida o comparador setorial com Pódio 5 Selos, Radar 5D e Dispersão 2x2."""
        resp = self.client.get("/api/fii/compare-sector/LOGISTICA")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("segment_code"), "LOGISTICA")
        self.assertEqual(len(data.get("podium", [])), 5)
        self.assertGreater(len(data.get("radar", [])), 0)
        self.assertGreater(len(data.get("scatter", [])), 0)
        self.assertGreater(len(data.get("matrix", [])), 0)
        print(f" -> [OK] Comparador Logística: Pódio de 5 selos, Radar e Matriz com {len(data['matrix'])} fundos.")

if __name__ == "__main__":
    print("=" * 70)
    print(" [TESTES] VALIDACAO DA API REST FASTAPI (TERMINAL FIIs)")
    print("=" * 70)
    unittest.main(verbosity=2)
