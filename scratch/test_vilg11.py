import json
from src.services.cross_validation_service import CrossValidationService
from src.services.report_generator import ReportGenerator
from src.services.fii_comparator_service import FIIComparatorService
from src.services.market_data import MarketDataService
from src.services.fundos_net_service import FundosNetService

def test_vilg11():
    ticker = "VILG11"
    print(f"=== TESTE COMPLETO DE DADOS E RELATÓRIO: {ticker} ===")
    
    # 1. Market Data
    md = MarketDataService.get_market_data(ticker)
    print("\n--- 1. Market Data (B3 / Yahoo / Brapi) ---")
    print(f"Preço Atual: R$ {md.get('current_price')}")
    print(f"P/VP Market: {md.get('pvp')}")
    print(f"DY 12M: {md.get('dy_12m')}%")
    print(f"Último Provento: R$ {md.get('last_dividend')}")
    print(f"VPC: R$ {md.get('vp_per_share')}")

    # 2. Fundos.NET (CVM)
    fnet = FundosNetService.get_latest_fii_data(ticker)
    print("\n--- 2. Fundos.NET / CVM Oficial ---")
    print(f"Razão Social: {fnet.get('razao_social')}")
    print(f"Gestor: {fnet.get('gestor')}")
    print(f"Administrador: {fnet.get('administrador')}")
    print(f"VPC Oficial: R$ {fnet.get('vpc')}")
    print(f"Patrimônio Líquido: R$ {fnet.get('patrimonio_liquido'):,}" if fnet.get('patrimonio_liquido') else "PL: None")
    print(f"Cotistas: {fnet.get('cotistas')}")
    print(f"Alavancagem PL: {fnet.get('alavancagem_pl_pct')}%")
    print(f"Data Referência: {fnet.get('data_referencia')}")
    print(f"Protocolo FNET: {fnet.get('data_protocolo_fnet')}")

    # 3. Cross Validation
    cross = CrossValidationService.validate_and_reconcile(ticker)
    print("\n--- 3. Validação Cruzada (Cross-Audit) ---")
    print(f"Segmento Detectado: {cross.get('segment_code')} - {cross.get('segment_name')}")
    print(f"BolsaAI Price: R$ {cross['bolsai'].get('price')}")
    print(f"BolsaAI P/VP: {cross['bolsai'].get('pvp')}")
    print(f"DY Recorrente: {cross['reconciliation'].get('dy_recorrente')}%")
    print(f"DY TTM: {cross['reconciliation'].get('dy_ttm')}%")
    print(f"Divergências Detectadas: {cross['reconciliation'].get('divergences')}")

    # 4. Geração do Relatório HTML
    rep = ReportGenerator.generate_html_report(ticker)
    print("\n--- 4. Dossiê HTML Gerado ---")
    print(f"Caminho do HTML: {rep.get('html_path')}")
    print(f"Score Técnico: {rep.get('score')}")
    print(f"Veredicto: {rep.get('veredicto')}")
    print(f"Preço Teto: R$ {rep.get('teto')}")
    print(f"P/VP no Retorno: {rep.get('pvp')}")
    print(f"DY Anual no Retorno: {rep.get('dy_anual')}%")
    print(f"Cotistas no Retorno: {rep.get('cotistas')}")

    # 5. Análise do Conteúdo do HTML
    with open(rep['html_path'], "r", encoding="utf-8") as f:
        html = f.read()

    from scratch.run_full_battery_test import extract_html_data
    price_html, pvp_html, vpc_html = extract_html_data(html)
    print("\n--- 5. Extração dos Cards do HTML ---")
    print(f"Cotação no HTML: {price_html}")
    print(f"VPC no HTML: {vpc_html}")
    print(f"P/VP no HTML: {pvp_html}")

    # 6. Comparador Setorial (Logística)
    comp = FIIComparatorService.compare_sector("LOGISTICA")
    df = comp["df"]
    vilg_row = df[df["ticker"] == "VILG11"]
    print("\n--- 6. Posição no Comparador de Logística ---")
    if not vilg_row.empty:
        v = vilg_row.iloc[0]
        print(f"Preço Mercado: R$ {v['preco_mercado']:.2f}")
        print(f"VPC: R$ {v['vpc']:.2f}")
        print(f"P/VP: {v['pvp']:.2f}")
        print(f"DY Anual: {v['dy_anual']:.2f}%")
        print(f"Retorno Real (IPCA+): {v['label_real_yield']}")
        print(f"Preço Teto Recomendado: R$ {v['preco_teto']:.2f}")
        print(f"Margem de Segurança: {v['margem_seguranca_pct']:+.1f}%")
        print(f"Cobertura FFO: {v['cobertura_ffo_pct']:.1f}%")
        print(f"Trend Status: {v['trend_status']}")
    
    print("\nPodium de Logística:")
    for k, p in comp["podium"].items():
        print(f"  {p['titulo']}: {p['ticker']} ({p['motivo']})")

if __name__ == '__main__':
    test_vilg11()
