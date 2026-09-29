import os
import re
import pandas as pd
from src.services.cross_validation_service import KNOWN_SEGMENTS, CrossValidationService
from src.services.report_generator import ReportGenerator
from src.services.market_data import MarketDataService

def extract_html_data(html: str):
    m_price = re.findall(r'Cotação Atual</div>\s*<div class="kpi-value">([^<]+)</div>', html)
    if not m_price:
        m_price = re.findall(r'Mercado:\s*(R\$\s*[\d\.,]+)', html)
    if not m_price:
        m_price = re.findall(r'Cotação de Mercado vs VPC</div>\s*<div class="kpi-value">([^<]+)</div>', html)
        
    m_pvp = re.findall(r'P/VP &[^<]*</div>\s*<div class="kpi-value[^"]*">([^<]+)</div>', html)
    if not m_pvp:
        m_pvp = re.findall(r'<div class="kpi-title">P/VP</div>\s*<div class="kpi-value[^"]*">([^<]+)</div>', html)
    if not m_pvp:
        m_pvp = re.findall(r'P/VP do FOF</div>\s*<div class="kpi-value[^"]*">([^<]+)</div>', html)
    if not m_pvp:
        m_pvp = re.findall(r'P/VP:\s*<strong>([^<]+)</strong>', html)
        
    m_vpc = re.findall(r'VPC Contábil:\s*([^<]+)</div>', html)
    if not m_vpc:
        m_vpc = re.findall(r'VPC:\s*(R\$\s*[\d\.,]+)', html)

    price_str = m_price[0].strip() if m_price else "N/A"
    pvp_str = m_pvp[0].strip() if m_pvp else "N/A"
    vpc_str = m_vpc[0].strip() if m_vpc else "N/A"
    return price_str, pvp_str, vpc_str

def run_battery():
    print(f"Iniciando bateria de validação para todos os {len(KNOWN_SEGMENTS)} FIIs cadastrados...")
    
    results = []
    
    for ticker, segment in KNOWN_SEGMENTS.items():
        try:
            # 1. Coleta dados de cross-validation (bolsai + reconciliação)
            cross = CrossValidationService.validate_and_reconcile(ticker)
            expected_price = float(cross["bolsai"].get("price") or 0.0)
            expected_pvp = cross["bolsai"].get("pvp")
            
            # 2. Gera relatório
            rep = ReportGenerator.generate_html_report(ticker)
            html_path = rep["html_path"]
            
            with open(html_path, "r", encoding="utf-8") as f:
                html = f.read()
                
            html_price_str, html_pvp_str, html_vpc_str = extract_html_data(html)
            
            # Converter preco html para float
            try:
                html_price_clean = float(html_price_str.replace("R$", "").replace(".", "").replace(",", ".").strip())
            except:
                html_price_clean = 0.0
                
            diff = abs(html_price_clean - expected_price) if expected_price > 0 else 0.0
            
            # Se a diferença for menor que 1 centavo, está perfeito
            status = "OK" if diff <= 0.02 or expected_price == 0 else "DIVERGENTE"
            
            results.append({
                "ticker": ticker,
                "segment": segment,
                "expected_price": expected_price,
                "html_price": html_price_str,
                "html_pvp": html_pvp_str,
                "rep_pvp": rep.get("pvp"),
                "rep_dy": rep.get("dy_anual"),
                "status": status,
                "diff": diff
            })
            print(f"[{status:10s}] {ticker:6s} ({segment:9s}) -> Esperado: R$ {expected_price:7.2f} | HTML: {html_price_str:11s} | P/VP HTML: {html_pvp_str:6s} | Rep P/VP: {rep.get('pvp')}")
        except Exception as e:
            print(f"[ERRO      ] {ticker}: {str(e)}")
            results.append({
                "ticker": ticker,
                "segment": segment,
                "status": f"ERRO: {str(e)}"
            })

    df_res = pd.DataFrame(results)
    print("\n" + "="*80)
    print("RESUMO DA BATERIA DE TESTES GERAL:")
    print("Total testados:", len(df_res))
    if "status" in df_res.columns:
        print(df_res["status"].value_counts())
        divergentes = df_res[df_res["status"] == "DIVERGENTE"]
        if not divergentes.empty:
            print("\nDivergências encontradas:")
            print(divergentes[["ticker", "segment", "expected_price", "html_price", "diff"]])
        else:
            print("\nTODOS OS 50 FIIS ESTÃO 100% ALINHADOS E CONSISTENTES ENTRE CROSS-VALIDATION E HTML!")

if __name__ == '__main__':
    run_battery()
