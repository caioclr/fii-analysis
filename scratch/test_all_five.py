import sys
sys.path.insert(0, ".")
from src.services.report_generator import ReportGenerator

tickers = ["HSML11", "XPML11", "VISC11", "HGBS11", "PMLL11"]
for t in tickers:
    res = ReportGenerator.generate_html_report(t)
    print(f"Ticker: {t:6s} | Seg: {res['segment_name']:20s} | Score: {res['score']} | Teto: R$ {res['teto']} | HTML lines: {len(res['html_content'].splitlines())}")
