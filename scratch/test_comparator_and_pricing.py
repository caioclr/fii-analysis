import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath("."))

from src.database.connection import init_db
from src.database.repository import (
    AuditHistoryRepository,
    GerencialHistoryRepository,
    PricingParametersRepository
)
from src.services.valuation_pricing_service import ValuationPricingService
from src.services.dividend_projection_service import DividendProjectionService
from src.services.trend_analysis_service import TrendAnalysisService
from src.services.fii_comparator_service import FIIComparatorService

def run_tests():
    print("=== 1. Testando Inicialização do Banco ===")
    init_db()
    params = PricingParametersRepository.get_parameters()
    print(f"Parâmetros macro carregados: {params}")
    assert "ntnb_reference_rate" in params
    assert params["ntnb_reference_rate"] == 6.50

    print("\n=== 2. Testando Valuation & Retorno Real (Sem Bazin) ===")
    real_y = ValuationPricingService.calculate_real_yield(
        ticker="XPML11",
        dy_anual=8.88,
        segment_code="SHOPPING"
    )
    print(f"Retorno Real XPML11: {real_y}")
    assert "IPCA + 8.88%" in real_y["label_real"]
    assert real_y["spread_vs_ntnb"] == round(8.88 - 6.50, 2)

    pricing_hsml = ValuationPricingService.calculate_consolidated_pricing(
        ticker="HSML11",
        metrics={
            "preco_mercado": 94.0,
            "vpc": 98.42,
            "provento_mes": 0.80,
            "ffo_cota": 0.82,
            "dy_anual": 10.21
        },
        segment_code="SHOPPING"
    )
    print(f"Consolidado Preço-Teto HSML11: {pricing_hsml}")
    assert pricing_hsml["preco_teto_recomendado"] > 0
    assert "margem_seguranca_pct" in pricing_hsml
    assert pricing_hsml["teto_spread_ntnb"] > 0
    assert pricing_hsml["teto_gordon"] > 0
    assert pricing_hsml["teto_patrimonial"] == 98.42

    print("\n=== 3. Testando Projeção de Dividendos & Reservas (Lei 8.668/93) ===")
    proj_hsml = DividendProjectionService.project_and_analyze(
        ticker="HSML11",
        ffo_cota=0.82,
        provento_atual=0.80,
        reserva_acumulada_cota=1.65,
        segment_code="SHOPPING"
    )
    print(f"Projeção HSML11: {proj_hsml}")
    assert proj_hsml["status_sustentabilidade"] == "Superávit Operacional"
    assert proj_hsml["meses_reserva_cobertura"] > 1.5
    assert proj_hsml["tem_potencial_extraordinario"] is True
    assert proj_hsml["extraordinario_estimado_fim_semestre"] > 0

    print("\n=== 4. Testando Análise de Tendência MoM ===")
    trend_xpml = TrendAnalysisService.analyze_ticker_trend("XPML11")
    print(f"Tendência XPML11: {trend_xpml['badge_geral']} (score={trend_xpml.get('score_trajetoria')})")
    assert trend_xpml["has_history"] is True
    assert len(trend_xpml["series"]) >= 2
    assert "deltas" in trend_xpml

    print("\n=== 5. Testando Comparador Setorial (Shopping) ===")
    comp_shop = FIIComparatorService.compare_sector("SHOPPING")
    print(f"FIIs comparados em Shopping: {len(comp_shop['items'])}")
    assert len(comp_shop["items"]) >= 5
    podium = comp_shop["podium"]
    print("Pódio Setorial:")
    for k, v in podium.items():
        print(f"  [{k}] {v['titulo']}: {v['ticker']} - {v['motivo']}")
    assert "melhor_preco" in podium
    assert "maior_renda" in podium
    assert "mais_seguro" in podium
    assert "maior_extraordinario" in podium
    assert "lider_geral" in podium

    print("\n=== 6. Testando AuditHistoryRepository ===")
    AuditHistoryRepository.save_audit_snapshot({
        "ticker": "XPML11",
        "audit_date": "2026-09-25",
        "score": 8.5,
        "veredicto": "Aprovado",
        "preco_mercado": 102.50,
        "preco_teto": 110.00,
        "dy_anual": 8.88,
        "real_yield_pct": 8.88,
        "pvp": 0.91,
        "ffo_cota": 0.85,
        "cobertura_ffo": 1.06,
        "reserva_cota": 1.50,
        "trend_status": "MELHORANDO",
        "notes": "Teste automatizado de snapshot"
    })
    hist = AuditHistoryRepository.get_audit_history("XPML11")
    print(f"Snapshots de XPML11 salvos: {len(hist)}")
    assert len(hist) >= 1
    assert hist[0]["ticker"] == "XPML11"
    assert hist[0]["score"] == 8.5

    print("\n✅ TODOS OS TESTES PASSARAM COM SUCESSO!")

if __name__ == "__main__":
    run_tests()
