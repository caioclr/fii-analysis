import sys
sys.path.insert(0, ".")
from src.services.cross_validation_service import KNOWN_SEGMENTS, CrossValidationService
from src.services.report_generator import FII_KNOWLEDGE_BASE
from src.services.market_data import MarketDataService

print(f"Checking {len(KNOWN_SEGMENTS)} known tickers for data consistency...\n")
results = []
for ticker, seg in sorted(KNOWN_SEGMENTS.items()):
    kb = FII_KNOWLEDGE_BASE.get(ticker, {})
    kb_price = kb.get("preco_mercado")
    kb_vpc = kb.get("vpc")
    kb_pvp = kb.get("pvp")
    kb_dy = kb.get("dy_anual")
    
    # Live market
    md = MarketDataService.get_market_data(ticker)
    live_price = md.get("current_price")
    live_dy = md.get("dy_12m")
    
    diff = round(live_price - kb_price, 2) if (live_price and kb_price) else None
    results.append({
        "ticker": ticker,
        "segment": seg,
        "kb_price": kb_price,
        "live_price": live_price,
        "diff": diff,
        "kb_vpc": kb_vpc,
        "kb_pvp": kb_pvp,
        "kb_dy": kb_dy,
        "live_dy": live_dy
    })

print(f"{'Ticker':7s} | {'Segmento':10s} | {'Preço KB':10s} | {'Preço Live':10s} | {'Diferença':10s} | {'Status'}")
print("-" * 75)
for r in results:
    p_kb = f"R$ {r['kb_price']:.2f}" if r['kb_price'] else "N/A"
    p_live = f"R$ {r['live_price']:.2f}" if r['live_price'] else "N/A"
    diff_str = f"R$ {r['diff']:+.2f}" if r['diff'] is not None else "N/A"
    status = "OK" if (r['diff'] is not None and abs(r['diff']) <= 1.0) else "DIVERGENTE"
    print(f"{r['ticker']:7s} | {r['segment']:10s} | {p_kb:10s} | {p_live:10s} | {diff_str:10s} | {status}")

discrepancies = [r for r in results if r['diff'] is not None and abs(r['diff']) > 1.0]
missing = [r for r in results if r['live_price'] is None or r['kb_price'] is None]
print(f"\nResumo:")
print(f"Total de FIIs analisados: {len(results)}")
print(f"FIIs com preço divergente (> R$ 1,00): {len(discrepancies)}")
print(f"FIIs com preço ausente: {len(missing)}")
